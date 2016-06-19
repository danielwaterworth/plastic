import bytecode
import struct

class BasicBlockConstructor(object):
    def __init__(self, function, index):
        self.function = function
        self.instructions = []
        self.terminal = None
        self.index = index

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    # Only available for constructor
    def special_phi(self, inputs):
        input_hash = {}
        for block, var in inputs:
            input_hash[block] = var
        instruction = bytecode.Phi(input_hash)
        self.instructions.append(instruction)
        return (self.function.create_variable(), instruction)

    def phi(self, inputs):
        return self.special_phi(inputs)[0]

    def constant_bool(self, value):
        self.instructions.append(bytecode.ConstantBool(value))
        return self.function.create_variable()

    def constant_uint(self, value):
        self.instructions.append(bytecode.ConstantUInt(value))
        return self.function.create_variable()

    def constant_byte(self, value):
        self.instructions.append(bytecode.ConstantByte(value))
        return self.function.create_variable()

    def constant_string(self, value):
        self.instructions.append(bytecode.ConstantString(value))
        return self.function.create_variable()

    def void(self):
        self.instructions.append(bytecode.Void())
        return self.function.create_variable()

    def operation(self, operator, arguments):
        self.instructions.append(bytecode.Operation(operator, arguments))
        return self.function.create_variable()

    def fun_call(self, function, arguments):
        self.instructions.append(bytecode.FunctionCall(function, arguments))
        return self.function.create_variable()

    def sys_call(self, function, arguments):
        self.instructions.append(bytecode.SysCall(function, arguments))
        return self.function.create_variable()

    def new_coroutine(self, function, arguments):
        self.instructions.append(bytecode.NewCoroutine(function, arguments))
        return self.function.create_variable()

    def load(self, address):
        self.instructions.append(bytecode.Load(address))
        return self.function.create_variable()

    def store(self, address, variable):
        self.instructions.append(bytecode.Store(address, variable))
        return self.function.create_variable()

    def run_coroutine(self, coroutine):
        self.instructions.append(bytecode.RunCoroutine(coroutine))
        return self.function.create_variable()

    def yield_(self, value):
        self.instructions.append(bytecode.Yield(value))
        return self.function.create_variable()

    def resume(self, coroutine, value):
        self.instructions.append(bytecode.Resume(coroutine, value))
        return self.function.create_variable()

    def ret(self, variable):
        self.terminal = bytecode.Return(variable)

    # Only available for constructor
    def special_goto(self, block):
        self.terminal = bytecode.Goto(block)
        return self.terminal

    def goto(self, block):
        self.special_goto(block)

    # Only available for constructor
    def special_conditional(self, variable, true_block, false_block):
        self.terminal = bytecode.Conditional(variable, true_block, false_block)
        return self.terminal

    def conditional(self, variable, true_block, false_block):
        self.special_conditional(variable, true_block, false_block)

    def catch_fire_and_die(self):
        self.terminal = bytecode.CatchFireAndDie()

    def get_basic_block(self):
        return bytecode.BasicBlock(self.instructions, self.terminal)

class FunctionConstructor(object):
    def __init__(self, name, num_arguments):
        self.name = name
        self.basic_blocks = []
        self.num_arguments = num_arguments
        self.next_variable = num_arguments

    def create_variable(self):
        n = self.next_variable
        self.next_variable += 1
        return n

    def __enter__(self):
        return (self, range(self.num_arguments))

    def __exit__(self, type, value, traceback):
        pass

    def basic_block(self):
        basic_block = BasicBlockConstructor(self, len(self.basic_blocks))
        self.basic_blocks.append(basic_block)
        return basic_block

    def get_function(self):
        basic_blocks = [basic_block.get_basic_block() for basic_block in self.basic_blocks]
        return bytecode.Function(self.name, self.num_arguments, basic_blocks)

class ProgramConstructor(object):
    def __init__(self):
        self.functions = []

    def function(self, name, num_arguments):
        function = FunctionConstructor(name, num_arguments)
        self.functions.append(function)
        return function

    def get_program(self):
        functions = [function.get_function() for function in self.functions]
        function_map = {}
        for function in functions:
            function_map[function.name] = function
        return bytecode.Program(function_map)

class BytecodeConstructor(object):
    def __init__(self):
        self.program = ProgramConstructor()

    def __enter__(self):
        return self.program

    def __exit__(self, type, value, traceback):
        pass

    def get_program(self):
        return self.program.get_program()
