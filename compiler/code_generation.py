import itertools
import struct
import program

class FunctionContext(object):
    def __init__(self, variables, blocks):
        self.variables = variables
        self.blocks = blocks

    def lookup_variable(self, name):
        return self.variables[name]

    def lookup_block(self, name):
        return self.blocks[name]

def create_function_context(function):
    assert len(function.parameters) == len(set(function.parameters))
    variables = dict(zip(function.parameters, itertools.count()))
    blocks = {}
    next_variable = len(function.parameters)

    for basic_block, basic_block_index in zip(function.basic_blocks, itertools.count()):
        if basic_block.label:
            assert not basic_block.label in blocks
            blocks[basic_block.label] = basic_block_index

        for phi_node in basic_block.phi_nodes:
            assert not phi_node.name in variables
            variables[phi_node.name] = next_variable
            next_variable += 1

        for statement in basic_block.statements:
            if isinstance(statement, program.Assignment):
                assert not statement.name in variables
                variables[statement.name] = next_variable
            next_variable += 1

    return FunctionContext(variables, blocks)

def generate_phi_node(writer, context, phi_node):
    items = [(context.lookup_block(block), context.lookup_variable(variable)) for block, variable in phi_node.items]
    writer.phi(items)

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

def generate_expression(writer, context, expression):
    if isinstance(expression, program.NumberLiteral):
        writer.constant(struct.pack('>Q', expression.n))
    elif isinstance(expression, program.Load):
        address = context.lookup_variable(expression.address)
        writer.load(address)
    elif isinstance(expression, program.BinOp):
        lhs = context.lookup_variable(expression.lhs)
        rhs = context.lookup_variable(expression.rhs)
        operator = operator_names[expression.operator]
        writer.operation(operator, [lhs, rhs])
    elif isinstance(expression, program.FunctionCallExpression):
        arguments = [context.lookup_variable(argument) for argument in expression.arguments]
        writer.fun_call(expression.name, arguments)
    elif isinstance(expression, program.SysCallExpression):
        arguments = [context.lookup_variable(argument) for argument in expression.arguments]
        writer.sys_call(expression.name, arguments)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(writer, context, statement):
    if isinstance(statement, program.Assignment):
        generate_expression(writer, context, statement.expression)
    elif isinstance(statement, program.FunctionCallStatement):
        arguments = [context.lookup_variable(argument) for argument in statement.arguments]
        writer.fun_call(statement.name, arguments)
    elif isinstance(statement, program.SysCallStatement):
        arguments = [context.lookup_variable(argument) for argument in statement.arguments]
        writer.sys_call(statement.name, arguments)
    elif isinstance(statement, program.Store):
        address = context.lookup_variable(statement.address)
        value = context.lookup_variable(statement.value)
        writer.store(address, value)
    else:
        raise NotImplementedError('unknown statement type: %s' % type(statement))

def generate_terminator(writer, context, terminator):
    if isinstance(terminator, program.Return):
        writer.ret(context.lookup_variable(terminator.variable))
    elif isinstance(terminator, program.Goto):
        writer.goto(context.lookup_block(terminator.block))
    elif isinstance(terminator, program.Condition):
        variable = context.lookup_variable(terminator.variable)
        true_block = context.lookup_block(terminator.true_block)
        false_block = context.lookup_block(terminator.false_block)
        writer.conditional(variable, true_block, false_block)
    else:
        raise NotImplementedError('unknown terminator type: %s' % type(terminator))

def generate_basic_block(writer, context, basic_block):
    with writer.basic_block() as basic_block_writer:
        for phi_node in basic_block.phi_nodes:
            generate_phi_node(basic_block_writer, context, phi_node)

        for statement in basic_block.statements:
            generate_statement(basic_block_writer, context, statement)

        generate_terminator(basic_block_writer, context, basic_block.terminator)

def generate_function(program_writer, function):
    with program_writer.function(function.name, len(function.parameters)) as (function_writer, _):
        context = create_function_context(function)
        for basic_block in function.basic_blocks:
            generate_basic_block(function_writer, context, basic_block)

def generate_code(writer, functions):
    with writer as program_writer:
        for function in functions:
            generate_function(program_writer, function)
