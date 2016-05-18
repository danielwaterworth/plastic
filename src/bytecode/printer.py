class BasicBlockPrinter(object):
    def __init__(self, function):
        self.function = function

    def __enter__(self):
        print "BASIC BLOCK START"
        return self

    def __exit__(self, type, value, traceback):
        if not value:
            print "BASIC BLOCK END"

    def constant(self, value):
        var = self.function.create_variable()
        print ("CONSTANT", value, var)
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

class FunctionPrinter(object):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
        self.next_variable = len(arguments)

    def create_variable(self):
        i = self.next_variable
        self.next_variable += 1
        return i

    def __enter__(self):
        print ("FUNCTION START", self.name, self.arguments)
        return self

    def __exit__(self, type, value, traceback):
        if not value:
            print "FUNCTION END"

    def basic_block(self):
        return BasicBlockPrinter(self)

class ProgramPrinter(object):
    def function(self, name, arguments):
        return FunctionPrinter(name, arguments)

class BytecodePrinter(object):
    def __enter__(self):
        print "PROGRAM START"
        return ProgramPrinter()

    def __exit__(self, type, value, traceback):
        if not value:
            print "PROGRAM END"
