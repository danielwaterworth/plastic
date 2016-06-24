def memoize(f):
    memo = {}
    def helper(*x):
        x = tuple(x)
        if x not in memo:
            memo[x] = f(*x)
        return memo[x]
    return helper

class BasicBlockOptimizer(object):
    def __init__(self, basic_block):
        self.basic_block = basic_block

    def __enter__(self):
        return self.basic_block.__enter__()

    def __exit__(self, type, value, traceback):
        return self.basic_block.__exit__(type, value, traceback)

    @property
    def index(self):
        return self.basic_block.index

    def phi(self, inputs):
        return self.basic_block.phi(inputs)

    def special_phi(self, inputs):
        return self.basic_block.special_phi(inputs)

    @memoize
    def constant_bool(self, value):
        return self.basic_block.constant_bool(value)

    @memoize
    def constant_byte(self, value):
        return self.basic_block.constant_byte(value)

    @memoize
    def constant_char(self, value):
        return self.basic_block.constant_char(value)

    @memoize
    def constant_bytestring(self, value):
        return self.basic_block.constant_bytestring(value)

    @memoize
    def constant_string(self, value):
        return self.basic_block.constant_string(value)

    @memoize
    def constant_uint(self, value):
        return self.basic_block.constant_uint(value)

    @memoize
    def constant_int(self, value):
        return self.basic_block.constant_int(value)

    @memoize
    def constant_double(self, value):
        return self.basic_block.constant_double(value)

    @memoize
    def void(self):
        return self.basic_block.void()

    def operation(self, name, arguments):
        return self.basic_block.operation(name, arguments)

    def sys_call(self, name, arguments):
        return self.basic_block.sys_call(name, arguments)

    def fun_call(self, name, arguments):
        return self.basic_block.fun_call(name, arguments)

    def debug(self, value):
        return self.basic_block.debug(value)

    def new_coroutine(self, name, arguments):
        return self.basic_block.new_coroutine(name, arguments)

    def load(self, address):
        return self.basic_block.load(address)

    def store(self, address, value):
        return self.basic_block.store(address, value)

    def get(self):
        return self.basic_block.get()

    def put(self, variable):
        return self.basic_block.put(variable)

    def run_coroutine(self, coroutine):
        return self.basic_block.run_coroutine(coroutine)

    def yield_(self, value):
        return self.basic_block.yield_(value)

    def resume(self, coroutine, value):
        return self.basic_block.resume(coroutine, value)

    def ret(self, variable):
        return self.basic_block.ret(variable)

    def goto(self, block):
        return self.basic_block.goto(block)

    def special_goto(self, block):
        return self.basic_block.special_goto(block)

    def conditional(self, variable, true_block, false_block):
        return self.basic_block.conditional(variable, true_block, false_block)

    def special_conditional(self, variable, true_block, false_block):
        return self.basic_block.special_conditional(variable, true_block, false_block)

    def catch_fire_and_die(self):
        return self.basic_block.catch_fire_and_die()

    def throw(self, exception):
        return self.basic_block.throw(exception)

class FunctionOptimizer(object):
    def __init__(self, function, name, num_arguments):
        self.function = function
        self.name = name
        self.num_arguments = num_arguments
        self.next_variable = num_arguments

    def __enter__(self):
        _, variables = self.function.__enter__()
        return (self, variables)

    def __exit__(self, type, value, traceback):
        return self.function.__exit__(type, value, traceback)

    def basic_block(self):
        return BasicBlockOptimizer(self.function.basic_block())

class ProgramOptimizer(object):
    def __init__(self, program):
        self.program = program

    def function(self, name, num_arguments):
        return FunctionOptimizer(self.program.function(name, num_arguments), name, num_arguments)

class BytecodeOptimizer(object):
    def __init__(self, program):
        self.program = program

    def __enter__(self):
        return ProgramOptimizer(self.program.__enter__())

    def __exit__(self, type, value, traceback):
        return self.program.__exit__(type, value, traceback)
