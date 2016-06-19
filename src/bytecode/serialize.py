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
    elif isinstance(instruction, bytecode.NewCoroutine):
        block_writer.new_coroutine(instruction.function, instruction.arguments)
    elif isinstance(instruction, bytecode.ConstantBool):
        block_writer.constant_bool(instruction.value)
    elif isinstance(instruction, bytecode.ConstantByte):
        block_writer.constant_byte(instruction.value)
    elif isinstance(instruction, bytecode.ConstantString):
        block_writer.constant_string(instruction.value)
    elif isinstance(instruction, bytecode.ConstantUInt):
        block_writer.constant_uint(instruction.value)
    elif isinstance(instruction, bytecode.Void):
        block_writer.void()
    elif isinstance(instruction, bytecode.Load):
        block_writer.load(instruction.address)
    elif isinstance(instruction, bytecode.Store):
        block_writer.store(instruction.address, instruction.variable)
    elif isinstance(instruction, bytecode.RunCoroutine):
        block_writer.run_coroutine(instruction.coroutine)
    elif isinstance(instruction, bytecode.Yield):
        block_writer.yield_(instruction.value)
    elif isinstance(instruction, bytecode.Resume):
        block_writer.resume(instruction.coroutine, instruction.value)
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
    elif isinstance(terminator, bytecode.CatchFireAndDie):
        block_writer.catch_fire_and_die()
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
            num_arguments = function.num_arguments
            with writer.function(name, num_arguments) as (function_writer, _):
                serialize_function(function_writer, function)
