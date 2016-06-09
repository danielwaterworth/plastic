class Program(object):
    def __init__(self, functions):
        self.functions = functions

class Function(object):
    def __init__(self, name, num_arguments, blocks):
        self.name = name
        self.num_arguments = num_arguments
        self.blocks = blocks

class BasicBlock(object):
    def __init__(self, instructions, terminator):
        self.instructions = instructions
        self.terminator = terminator

class Instruction(object):
    pass

class Phi(Instruction):
    def __init__(self, inputs):
        self.inputs = inputs

class FunctionCall(Instruction):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class SysCall(Instruction):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class Constant(Instruction):
    def __init__(self, value):
        self.value = value

class Load(Instruction):
    def __init__(self, address, size):
        self.address = address
        self.size = size

class Store(Instruction):
    def __init__(self, address, value):
        self.address = address
        self.value = value

class Terminator(object):
    pass

class Return(Terminator):
    def __init__(self, variable):
        self.variable = variable

class Goto(Terminator):
    def __init__(self, block_index):
        self.block_index = block_index

class Conditional(Terminator):
    def __init__(self, condition_variable, true_block, false_block):
        self.condition_variable = condition_variable
        self.true_block = true_block
        self.false_block = false_block
