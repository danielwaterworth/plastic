import bytecode

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

    def constant(self, value):
        self.instructions.append(bytecode.Constant(value))
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

    def load(self, address):
        self.instructions.append(bytecode.Load(address))
        return self.function.create_variable()

    def store(self, address, variable):
        self.instructions.append(bytecode.Store(address, variable))
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

    def get_basic_block(self):
        return bytecode.BasicBlock(self.instructions, self.terminal)

class FunctionConstructor(object):
    def __init__(self, name, argument_sizes, return_size):
        self.name = name
        self.basic_blocks = []
        self.argument_sizes = argument_sizes
        self.return_size = return_size
        self.next_variable = len(argument_sizes)

    def create_variable(self):
        n = self.next_variable
        self.next_variable += 1
        return n

    def __enter__(self):
        return (self, range(len(self.argument_sizes)))

    def __exit__(self, type, value, traceback):
        pass

    def basic_block(self):
        basic_block = BasicBlockConstructor(self, len(self.basic_blocks))
        self.basic_blocks.append(basic_block)
        return basic_block

    def get_function(self):
        basic_blocks = [basic_block.get_basic_block() for basic_block in self.basic_blocks]
        return bytecode.Function(self.name, self.argument_sizes, self.return_size, basic_blocks)

class ProgramConstructor(object):
    def __init__(self):
        self.functions = []

    def function(self, name, argument_sizes, return_size):
        function = FunctionConstructor(name, argument_sizes, return_size)
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
