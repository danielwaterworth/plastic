import itertools
import struct
import program

sys_call_signatures = {
    'print_num': ([program.uint], program.void)
}

class GenerationContext(object):
    def __init__(self, function_signatures, function_writer, basic_block, variables):
        self.function_signatures = function_signatures
        self.function_writer = function_writer
        self.basic_block = basic_block
        self.variables = variables

    def add(self, name, variable, type):
        if name in self.variables:
            assert type == self.variables[name][1]
        self.variables[name] = (variable, type)

    def lookup(self, name):
        return self.variables[name]

comparison_operators = {
    '<': 'lt',
    '>': 'gt',
    '<=': 'le',
    '>=': 'ge'
}

arithmetic_operators = {
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div'
}

def operator_name_and_type(operator, rhs_type, lhs_type):
    if operator in comparison_operators:
        assert rhs_type == program.uint
        assert lhs_type == program.uint
        return (comparison_operators[operator], program.bool)
    elif operator in ['==', '!=']:
        assert lhs_type == program.uint
        assert rhs_type == program.uint
        if operator == '==':
            return ('eq', program.bool)
        else:
            return ('ne', program.bool)
    elif operator in arithmetic_operators:
        return (arithmetic_operators[operator], program.uint)

def process_arguments(signature, context, arguments):
    data = [generate_expression(context, argument) for argument in arguments]
    assert signature[0] == [d[1] for d in data]
    arguments = [d[0] for d in data]
    return (arguments, signature[1])

def generate_expression(context, expression):
    if isinstance(expression, program.Variable):
       return context.lookup(expression.name)
    elif isinstance(expression, program.NumberLiteral):
        return (context.basic_block.constant(struct.pack('>Q', expression.n)), program.uint)
    elif isinstance(expression, program.BoolLiteral):
        return (context.basic_block.constant(struct.pack('>B', 1 if expression.b else 0)), program.bool)
    elif isinstance(expression, program.Load):
        address, address_type = generate_expression(context, expression.address)
        assert address_type == program.uint
        return (context.basic_block.load(address), program.uint)
    elif isinstance(expression, program.BinOp):
        lhs, lhs_type = generate_expression(context, expression.lhs)
        rhs, rhs_type = generate_expression(context, expression.rhs)
        operator, output_type = operator_name_and_type(expression.operator, lhs_type, rhs_type)
        return (context.basic_block.operation(operator, [lhs, rhs]), output_type)
    elif isinstance(expression, program.FunctionCallExpression):
        signature = context.function_signatures[expression.name]
        arguments, output_type = process_arguments(signature, context, expression.arguments)
        return (context.basic_block.fun_call(expression.name, arguments), output_type)
    elif isinstance(expression, program.SysCallExpression):
        signature = sys_call_signatures[expression.name]
        arguments, output_type = process_arguments(signature, context, expression.arguments)
        return (context.basic_block.sys_call(expression.name, arguments), output_type)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(context, statement):
    if isinstance(statement, program.Assignment):
        (var, type) = generate_expression(context, statement.expression)
        context.add(statement.name, var, type)
    elif isinstance(statement, program.FunctionCallStatement):
        signature = context.function_signatures[statement.name]
        arguments, _ = process_arguments(signature, context, statement.arguments)
        context.basic_block.fun_call(statement.name, arguments)
    elif isinstance(statement, program.SysCallStatement):
        signature = sys_call_signatures[statement.name]
        arguments, _ = process_arguments(signature, context, statement.arguments)
        context.basic_block.sys_call(statement.name, arguments)
    elif isinstance(statement, program.Store):
        address, address_type = generate_expression(context, statement.address)
        assert address_type == program.uint
        value, value_type = generate_expression(context, statement.value)
        assert value_type == program.uint
        context.basic_block.store(address, value)
    elif isinstance(statement, program.Conditional):
        # FIXME
        assert not statement.true_block.ret
        assert not statement.false_block.ret

        condition_variable, condition_type = generate_expression(context, statement.expression)
        assert condition_type == program.bool
        entry_conditional = context.basic_block.special_conditional(condition_variable, 0, 0)

        true_block = context.function_writer.basic_block()
        entry_conditional.true_block = true_block.index
        true_context = GenerationContext(context.function_signatures, context.function_writer, true_block, dict(context.variables))

        for true_statement in statement.true_block.statements:
            generate_statement(true_context, true_statement)

        last_true_block = true_context.basic_block.index
        true_goto = true_context.basic_block.special_goto(0)

        false_block = context.function_writer.basic_block()
        entry_conditional.false_block = false_block.index
        false_context = GenerationContext(context.function_signatures, context.function_writer, false_block, dict(context.variables))

        for false_statement in statement.false_block.statements:
            generate_statement(false_context, false_statement)

        last_false_block = false_context.basic_block.index
        false_goto = false_block.special_goto(0)

        context.basic_block = context.function_writer.basic_block()
        true_goto.block_index = context.basic_block.index
        false_goto.block_index = context.basic_block.index

        variables = {}
        for variable in set(true_context.variables.keys()) & set(false_context.variables.keys()):
            true_variable = true_context.lookup(variable)
            false_variable = false_context.lookup(variable)
            if true_variable == false_variable:
                variables[variable] = true_variable
            else:
                phi_inputs = [(last_true_block, true_variable), (last_false_block, false_variable)]
                variables[variable] = (context.basic_block.phi(phi_inputs), context.lookup(variable)[1])

        context.variables = variables
    elif isinstance(statement, program.While):
        assert not statement.body.ret

        current_index = context.basic_block.index
        entry_goto = context.basic_block.special_goto(0)
        context.basic_block = context.function_writer.basic_block()
        entry_goto.block_index = context.basic_block.index

        variables = {}
        phis = {}
        for name, (variable, variable_type) in context.variables.iteritems():
            inputs = [(current_index, variable)]
            variable, phi = context.basic_block.special_phi(inputs)
            phis[name] = phi
            variables[name] = (variable, variable_type)
        context.variables = variables

        for body_statement in statement.body.statements:
            generate_statement(context, body_statement)

        last_body_index = context.basic_block.index

        for name, phi in phis.iteritems():
            phi.inputs[last_body_index] = context.lookup(name)[0]

        condition_variable, condition_type = generate_expression(context, statement.expression)
        assert condition_type == program.bool
        body_conditional = context.basic_block.special_conditional(condition_variable, last_body_index, 0)
        context.basic_block = context.function_writer.basic_block()
        body_conditional.false_block = context.basic_block.index
    else:
        raise NotImplementedError('unknown statement type: %s' % type(statement))

def generate_function(function_signatures, program_writer, function):
    parameter_names = [parameter[0] for parameter in function.parameters]
    parameter_types = [parameter[1] for parameter in function.parameters]
    parameter_sizes = [parameter[1].size for parameter in function.parameters]
    return_size = function.return_type.size
    with program_writer.function(function.name, parameter_sizes, return_size) as (function_writer, variables):
        variables = dict(zip(parameter_names, zip(variables, parameter_types)))
        basic_block = function_writer.basic_block()
        context = GenerationContext(function_signatures, function_writer, basic_block, variables)

        for statement in function.body.statements:
            generate_statement(context, statement)

        if function.body.ret:
            variable, variable_type = generate_expression(context, function.body.ret.expression)
            assert variable_type == function.return_type
            context.basic_block.ret(variable)

def generate_code(writer, functions):
    function_signatures = {}
    for function in functions:
        assert not function.name in function_signatures
        arg_types = [arg[1] for arg in function.parameters]
        function_signatures[function.name] = (arg_types, function.return_type)

    with writer as program_writer:
        for function in functions:
            generate_function(function_signatures, program_writer, function)
