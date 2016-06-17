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

    def ret(self, variable):
        print ("RET", variable)

    def goto(self, block):
        print ("GOTO", block)

    def conditional(self, variable, true_block, false_block):
        print ("CONDITIONAL", variable, true_block, false_block)

    def catch_fire_and_die(self):
        print "CATCH_FIRE_AND_DIE"

class FunctionPrinter(object):
    def __init__(self, name, argument_sizes, return_size):
        self.name = name
        self.argument_sizes = argument_sizes
        self.return_size = return_size
        self.next_variable = len(argument_sizes)

    def create_variable(self):
        i = self.next_variable
        self.next_variable += 1
        return i

    def __enter__(self):
        print ("FUNCTION START", self.name, self.argument_sizes, self.return_size)
        return (self, [i for i in xrange(len(self.argument_sizes))])

    def __exit__(self, type, value, traceback):
        if not value:
            print "FUNCTION END"

    def basic_block(self):
        return BasicBlockPrinter(self)

class ProgramPrinter(object):
    def function(self, name, argument_sizes, return_size):
        return FunctionPrinter(name, argument_sizes, return_size)

class BytecodePrinter(object):
    def __enter__(self):
        print "PROGRAM START"
        return ProgramPrinter()

    def __exit__(self, type, value, traceback):
        if not value:
            print "PROGRAM END"
