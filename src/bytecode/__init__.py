from rpython.rlib.jit import purefunction

class Program(object):
    def __init__(self, functions):
        self.functions = functions

    @purefunction
    def get_function(self, function):
        return self.functions[function]

class Function(object):
    _immutable_fields_ = ['name', 'num_arguments', 'num_return_values', 'blocks[*]']
    def __init__(self, name, num_arguments, num_return_values, blocks):
        self.name = name
        self.num_arguments = num_arguments
        self.num_return_values = num_return_values
        self.blocks = list(blocks)

    @purefunction
    def num_blocks(self):
        return len(self.blocks)

    @purefunction
    def get_block(self, i):
        return self.blocks[i]

    @purefunction
    def get_block_value_offset(self, i):
        return self.block_value_offsets[i]

class BasicBlock(object):
    _immutable_fields_ = ['terminator', 'instructions[*]']
    def __init__(self, instructions, terminator):
        self.instructions = list(instructions)
        self.terminator = terminator

    @purefunction
    def num_instructions(self):
        return len(self.instructions)

    @purefunction
    def get_instruction(self, i):
        return self.instructions[i]

class Instruction(object):
    pass

class Phi(Instruction):
    def __init__(self, inputs):
        self.inputs = inputs

    @purefunction
    def get_input(self, i):
        return self.inputs[i]

class Copy(Instruction):
    pass

class Move(Instruction):
    _immutable_fields_ = ['variable']
    def __init__(self, variable):
        self.variable = variable

class Unpack(Instruction):
    pass

class Operation(Instruction):
    _immutable_fields_ = ['operator', 'arguments[*]']
    def __init__(self, operator, arguments):
        self.operator = operator
        self.arguments = list(arguments)

class FunctionCall(Instruction):
    _immutable_fields_ = ['function', 'arguments[*]']
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = list(arguments)

class SysCall(Instruction):
    _immutable_fields_ = ['function', 'arguments[*]']
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = list(arguments)

class NewCoroutine(Instruction):
    _immutable_fields_ = ['function', 'arguments[*]']
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = list(arguments)

class Debug(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantBool(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantByte(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantChar(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantByteString(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantString(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantInt(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantUInt(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class ConstantDouble(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class Void(Instruction):
    pass

class Load(Instruction):
    _immutable_fields_ = ['address']
    def __init__(self, address):
        self.address = address

class Store(Instruction):
    _immutable_fields_ = ['address', 'variable']
    def __init__(self, address, variable):
        self.address = address
        self.variable = variable

class Get(Instruction):
    pass

class Put(Instruction):
    _immutable_fields_ = ['variable']
    def __init__(self, variable):
        self.variable = variable

class RunCoroutine(Instruction):
    _immutable_fields_ = ['coroutine']
    def __init__(self, coroutine):
        self.coroutine = coroutine

class Yield(Instruction):
    _immutable_fields_ = ['value']
    def __init__(self, value):
        self.value = value

class Resume(Instruction):
    _immutable_fields_ = ['coroutine', 'value']
    def __init__(self, coroutine, value):
        self.coroutine = coroutine
        self.value = value

class Terminator(object):
    pass

class Return(Terminator):
    _immutable_fields_ = ['variables[*]']
    def __init__(self, variables):
        self.variables = list(variables)

class Goto(Terminator):
    _immutable_fields_ = ['block_index']
    def __init__(self, block_index):
        self.block_index = block_index

class Conditional(Terminator):
    _immutable_fields_ = ['condition_variable', 'true_block', 'false_block']
    def __init__(self, condition_variable, true_block, false_block):
        self.condition_variable = condition_variable
        self.true_block = true_block
        self.false_block = false_block

class CatchFireAndDie(Terminator):
    pass

class Throw(Terminator):
    _immutable_fields_ = ['exception']
    def __init__(self, exception):
        self.exception = exception
