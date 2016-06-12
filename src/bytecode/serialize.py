import bytecode

def serialize_instruction(block_writer, instruction):
    if isinstance(instruction, bytecode.Phi):
        block_writer.phi(instruction.inputs.items())
    elif isinstance(instruction, bytecode.Operation):
        block_writer.operation(instruction.operator, instruction.arguments)
    elif isinstance(instruction, bytecode.FunctionCall):
        block_writer.fun_call(instruction.function, instruction.arguments)
    elif isinstance(instruction, bytecode.SysCall):
        block_writer.sys_call(instruction.function, instruction.arguments)
    elif isinstance(instruction, bytecode.Constant):
        block_writer.constant(instruction.value)
    elif isinstance(instruction, bytecode.Load):
        block_writer.load(instruction.address)
    elif isinstance(instruction, bytecode.Store):
        block_writer.store(instruction.address, instruction.variable)
    else:
        raise NotImplementedError('unknown instruction type: %s' % type(instruction))

def serialize_terminator(block_writer, terminator):
    if isinstance(terminator, bytecode.Return):
        block_writer.ret(terminator.variable)
    elif isinstance(terminator, bytecode.Goto):
        block_writer.goto(terminator.block_index)
    elif isinstance(terminator, bytecode.Conditional):
        variable = terminator.condition_variable
        true_block = terminator.true_block
        false_block = terminator.false_block
        block_writer.conditional(variable, true_block, false_block)
    else:
        raise NotImplementedError('unknown terminator type: %s' % type(terminator))

def serialize_block(block_writer, block):
    for instruction in block.instructions:
        serialize_instruction(block_writer, instruction)

    serialize_terminator(block_writer, block.terminator)

def serialize_function(function_writer, function):
    for block in function.blocks:
        with function_writer.basic_block() as block_writer:
            serialize_block(block_writer, block)

def serialize_program(program_writer, program):
    with program_writer as writer:
        for name, function in program.functions.iteritems():
            argument_sizes = function.argument_sizes
            with writer.function(name, argument_sizes) as (function_writer, _):
                serialize_function(function_writer, function)
