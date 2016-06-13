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

operators = {
    '<': 'lt',
    '>': 'gt',
    '<=': 'le',
    '>=': 'ge',
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '==': 'eq',
    '!=': 'ne'
}

def generate_expression(context, expression):
    if isinstance(expression, program.Variable):
        return context.lookup(expression.name)
    elif isinstance(expression, program.NumberLiteral):
        return context.basic_block.constant(struct.pack('>Q', expression.n))
    elif isinstance(expression, program.BoolLiteral):
        return context.basic_block.constant(struct.pack('>B', 1 if expression.b else 0))
    elif isinstance(expression, program.Load):
        address = generate_expression(context, expression.address)
        return context.basic_block.load(address)
    elif isinstance(expression, program.AttrLoad):
        return context.lookup('@%s' % expression.attr)
    elif isinstance(expression, program.BinOp):
        lhs = generate_expression(context, expression.lhs)
        rhs = generate_expression(context, expression.rhs)
        operator = operators[expression.operator]
        return context.basic_block.operation(operator, [lhs, rhs])
    elif isinstance(expression, program.FunctionCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.fun_call(expression.name, arguments)
    elif isinstance(expression, program.SysCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.sys_call(expression.name, arguments)
    elif isinstance(expression, program.MethodCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        object_variable = generate_expression(context, expression.obj)
        return expression.obj.type.method(context.basic_block, object_variable, expression.name, arguments)
    elif isinstance(expression, program.ConstructorCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.fun_call('%s.%s' % (expression.ty, expression.name), arguments)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(context, statement):
    if isinstance(statement, program.Assignment):
        var = generate_expression(context, statement.expression)
        context.add(statement.name, var)
    elif isinstance(statement, program.Store):
        address = generate_expression(context, statement.address)
        value = generate_expression(context, statement.value)
        context.basic_block.store(address, value)
    elif isinstance(statement, program.AttrStore):
        var = generate_expression(context, statement.value)
        context.add('@%s' % statement.attr, var)
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
    elif isinstance(statement, program.Expression):
        generate_expression(context, statement)
    else:
        raise NotImplementedError('unknown statement type: %s' % type(statement))

def generate_code_block(context, code_block):
    for statement in code_block.statements:
        generate_statement(context, statement)

    if code_block.ret:
        variable = generate_expression(context, code_block.ret.expression)
        context.basic_block.ret(variable)

def generate_function(program_writer, function):
    parameter_names = [parameter[0] for parameter in function.parameters]
    parameter_sizes = [parameter[1].size for parameter in function.parameters]
    return_size = function.return_type.size
    with program_writer.function(function.name, parameter_sizes, return_size) as (function_writer, variables):
        variables = dict(zip(parameter_names, variables))
        basic_block = function_writer.basic_block()
        context = GenerationContext(function_writer, basic_block, variables)

        generate_code_block(context, function.body)

def generate_record(program_writer, record):
    def generate_constructor(constructor):
        assert not constructor.body.ret

        function_name = '%s.%s' % (record.name, constructor.name)
        parameter_names = [parameter[0] for parameter in constructor.parameters]
        parameter_sizes = [parameter[1].size for parameter in constructor.parameters]
        return_size = record.type.size
        with program_writer.function(function_name, parameter_sizes, return_size) as (function_writer, variables):
            variables = dict(zip(parameter_names, variables))
            basic_block = function_writer.basic_block()
            context = GenerationContext(function_writer, basic_block, variables)

            generate_code_block(context, constructor.body)

            arguments = [context.lookup('@%s' % attr) for attr, _ in record.type.attrs]
            result = context.basic_block.operation('pack', arguments)
            context.basic_block.ret(result)

    def generate_method(method):
        function_name = '%s#%s' % (record.name, method.name)
        parameter_names = [parameter[0] for parameter in method.parameters]
        parameter_sizes = [record.type.size] + [parameter[1].size for parameter in method.parameters]
        return_size = method.return_type.size
        with program_writer.function(function_name, parameter_sizes, return_size) as (function_writer, variables):
            basic_block = function_writer.basic_block()

            variable_dict = dict(zip(parameter_names, variables[1:]))
            offset = 0
            offset_var = basic_block.constant(struct.pack('>Q', offset))
            for attr, attr_type in record.type.attrs:
                offset += attr_type.size
                new_offset_var = basic_block.constant(struct.pack('>Q', offset))
                var = basic_block.operation('slice', [offset_var, new_offset_var, variables[0]])
                variable_dict['@%s' % attr] = var
                offset_var = new_offset_var

            context = GenerationContext(function_writer, basic_block, variable_dict)

            generate_code_block(context, method.body)

    for decl in record.decls:
        if isinstance(decl, program.Constructor):
            generate_constructor(decl)
        elif isinstance(decl, program.Method):
            generate_method(decl)

def generate_code(writer, decls):
    with writer as program_writer:
        for decl in decls:
            if isinstance(decl, program.Function):
                generate_function(program_writer, decl)
            elif isinstance(decl, program.Record):
                generate_record(program_writer, decl)
            else:
                raise NotImplementedError('unknown top level decl: %s' % type(decl))
