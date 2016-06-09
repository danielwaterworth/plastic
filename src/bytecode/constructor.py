import bytecode

class BasicBlockConstructor(object):
    def __init__(self, function):
        self.function = function
        self.instructions = []
        self.terminal = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def constant(self, value):
        self.instructions.append(bytecode.Constant(value))
        return self.function.create_variable()

    def fun_call(self, function, arguments):
        self.instructions.append(bytecode.FunctionCall(function, arguments))
        return self.function.create_variable()

    def sys_call(self, function, arguments):
        self.instructions.append(bytecode.SysCall(function, arguments))
        return self.function.create_variable()

    def ret(self, variable):
        self.terminal = bytecode.Return(variable)

    def goto(self, block):
        self.terminal = bytecode.Goto(block)

    def conditional(self, variable, true_block, false_block):
        self.terminal = bytecode.Conditional(variable, true_block, false_block)

    def get_basic_block(self):
        return bytecode.BasicBlock([], self.instructions, self.terminal)

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
        basic_block = BasicBlockConstructor(self)
        self.basic_blocks.append(basic_block)
        return basic_block

    def get_function(self):
        basic_blocks = [basic_block.get_basic_block() for basic_block in self.basic_blocks]
        return bytecode.Function(self.name, self.num_arguments, basic_blocks)

class ProgramConstructor(object):
    def __init__(self):
        self.functions = []

    def function(self, name, arguments):
        function = FunctionConstructor(name, arguments)
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
