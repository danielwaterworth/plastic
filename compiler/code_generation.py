import itertools
import struct
import program

class GenerationContext(object):
    def __init__(self, function_writer, basic_block, variables):
        self.function_writer = function_writer
        self.basic_block = basic_block
        self.variables = variables

    def add(self, name, variable):
        self.variables[name] = variable

    def lookup(self, name):
        return self.variables[name]

operator_names = {
    '<': 'lt',
    '>': 'gt',
    '<=': 'le',
    '>=': 'ge',
    '==': 'eq',
    '!=': 'ne',
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div'
}

def generate_expression(context, expression):
    if isinstance(expression, program.Variable):
       return context.lookup(expression.name)
    elif isinstance(expression, program.NumberLiteral):
        return context.basic_block.constant(struct.pack('>Q', expression.n))
    elif isinstance(expression, program.BoolLiteral):
        return context.basic_block.constant(struct.pack('>B', 1 if expression.b else 0))
    elif isinstance(expression, program.Load):
        address = context.lookup(expression.address)
        return context.basic_block.load(address)
    elif isinstance(expression, program.BinOp):
        lhs = context.lookup(expression.lhs)
        rhs = context.lookup(expression.rhs)
        operator = operator_names[expression.operator]
        return context.basic_block.operation(operator, [lhs, rhs])
    elif isinstance(expression, program.FunctionCallExpression):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.fun_call(expression.name, arguments)
    elif isinstance(expression, program.SysCallExpression):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.sys_call(expression.name, arguments)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(context, statement):
    if isinstance(statement, program.Assignment):
        var = generate_expression(context, statement.expression)
        context.add(statement.name, var)
    elif isinstance(statement, program.FunctionCallStatement):
        arguments = [generate_expression(context, argument) for argument in statement.arguments]
        context.basic_block.fun_call(statement.name, arguments)
    elif isinstance(statement, program.SysCallStatement):
        arguments = [generate_expression(context, argument) for argument in statement.arguments]
        context.basic_block.sys_call(statement.name, arguments)
    elif isinstance(statement, program.Store):
        address = context.lookup(statement.address)
        value = context.lookup(statement.value)
        context.basic_block.store(address, value)
    elif isinstance(statement, program.Conditional):
        # FIXME
        assert not statement.true_block.ret
        assert not statement.false_block.ret

        condition_variable = generate_expression(context, statement.expression)
        entry_conditional = context.basic_block.special_conditional(condition_variable, 0, 0)

        true_block = context.function_writer.basic_block()
        entry_conditional.true_block = true_block.index
        true_context = GenerationContext(context.function_writer, true_block, dict(context.variables))

        for true_statement in statement.true_block.statements:
            generate_statement(true_context, true_statement)

        last_true_block = true_context.basic_block.index
        true_goto = true_context.basic_block.special_goto(0)

        false_block = context.function_writer.basic_block()
        entry_conditional.false_block = false_block.index
        false_context = GenerationContext(context.function_writer, false_block, dict(context.variables))

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
                variables[variable] = context.basic_block.phi([(last_true_block, true_variable), (last_false_block, false_variable)])

        context.variables = variables
    elif isinstance(statement, program.While):
        assert not statement.body.ret

        current_index = context.basic_block.index
        entry_goto = context.basic_block.special_goto(0)
        context.basic_block = context.function_writer.basic_block()
        entry_goto.block_index = context.basic_block.index

        variables = {}
        phis = {}
        for name, variable in context.variables.iteritems():
            inputs = [(current_index, variable)]
            variable, phi = context.basic_block.special_phi(inputs)
            phis[name] = phi
            variables[name] = variable
        context.variables = variables

        for body_statement in statement.body.statements:
            generate_statement(context, body_statement)

        last_body_index = context.basic_block.index

        for name, phi in phis.iteritems():
            phi.inputs[last_body_index] = context.lookup(name)

        condition_variable = generate_expression(context, statement.expression)
        body_conditional = context.basic_block.special_conditional(condition_variable, last_body_index, 0)
        context.basic_block = context.function_writer.basic_block()
        body_conditional.false_block = context.basic_block.index
    else:
        raise NotImplementedError('unknown statement type: %s' % type(statement))

def generate_function(program_writer, function):
    parameter_names = [parameter[0] for parameter in function.parameters]
    parameter_sizes = [parameter[1] for parameter in function.parameters]
    return_size = function.return_size
    with program_writer.function(function.name, parameter_sizes, return_size) as (function_writer, variables):
        variables = dict(zip(parameter_names, variables))
        basic_block = function_writer.basic_block()
        context = GenerationContext(function_writer, basic_block, variables)

        for statement in function.body.statements:
            generate_statement(context, statement)

        if function.body.ret:
            variable = generate_expression(context, function.body.ret.expression)
            context.basic_block.ret(variable)

def generate_code(writer, functions):
    with writer as program_writer:
        for function in functions:
            generate_function(program_writer, function)
