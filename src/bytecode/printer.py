class BasicBlockPrinter(object):
    def __init__(self, function):
        self.function = function

    def __enter__(self):
        print "BASIC BLOCK START"
        return self

    def __exit__(self, type, value, traceback):
        if not value:
            print "BASIC BLOCK END"

    def phi(self, inputs):
        var = self.function.create_variable()
        print ("PHI", inputs, var)
        return var

    def constant(self, value):
        var = self.function.create_variable()
        print ("CONSTANT", value, var)
        return var

    def operation(self, name, arguments):
        var = self.function.create_variable()
        print ("OPERATION", name, arguments, var)
        return var

    def sys_call(self, name, arguments):
        var = self.function.create_variable()
        print ("SYS_CALL", name, arguments, var)
        return var

    def fun_call(self, name, arguments):
        var = self.function.create_variable()
        print ("FUN_CALL", name, arguments, var)
        return var

    def new_coroutine(self, name, arguments):
        var = self.function.create_variable()
        print ("NEW_COROUTINE", name, arguments, var)
        return var

    def load(self, address, size):
        var = self.function.create_variable()
        print ("LOAD", address, size, var)
        return var

    def store(self, address, value):
        var = self.function.create_variable()
        print ("STORE", address, value, var)
        return var

    def run_coroutine(self, coroutine):
        var = self.function.create_variable()
        print ("RUN_COROUTINE", coroutine, var)
        return var

    def yield_(self, value):
        var = self.function.create_variable()
        print ("YIELD", value, var)
        return var

    def resume(self, coroutine, value):
        var = self.function.create_variable()
        print ("RESUME", coroutine, value, var)
        return var

    def ret(self, variable):
        print ("RET", variable)

    def goto(self, block):
        print ("GOTO", block)

    def conditional(self, variable, true_block, false_block):
        print ("CONDITIONAL", variable, true_block, false_block)

    def catch_fire_and_die(self):
        print "CATCH_FIRE_AND_DIE"

class FunctionPrinter(object):
    def __init__(self, name, num_arguments, return_size):
        self.name = name
        self.num_arguments = num_arguments
        self.return_size = return_size
        self.next_variable = num_arguments

    def create_variable(self):
        i = self.next_variable
        self.next_variable += 1
        return i

    def __enter__(self):
        print ("FUNCTION START", self.name, self.num_arguments, self.return_size)
        return (self, [i for i in xrange(self.num_arguments)])

    def __exit__(self, type, value, traceback):
        if not value:
            print "FUNCTION END"

    def basic_block(self):
        return BasicBlockPrinter(self)

class ProgramPrinter(object):
    def function(self, name, num_arguments, return_size):
        return FunctionPrinter(name, num_arguments, return_size)

class BytecodePrinter(object):
    def __enter__(self):
        print "PROGRAM START"
        return ProgramPrinter()

    def __exit__(self, type, value, traceback):
        if not value:
            print "PROGRAM END"
