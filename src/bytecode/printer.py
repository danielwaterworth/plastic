class Variable(object):
    pass

class Concrete(Variable):
    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return "<Var %i>" % self.n

class Forward(Variable):
    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return "<Forward %i>" % self.n

    def assign(self, var):
        assert isinstance(var, Concrete)
        print ("ASSIGN_FORWARD", self.n, var.n)

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

    def forward(self):
        return self.function.create_forward()

class FunctionPrinter(object):
    def __init__(self, name, num_arguments):
        self.name = name
        self.num_arguments = num_arguments
        self.next_variable = num_arguments
        self.next_forward = 0

    def create_variable(self):
        i = self.next_variable
        self.next_variable += 1
        return Concrete(i)

    def create_forward(self):
        i = self.next_forward
        self.next_forward += 1
        return Forward(i)

    def __enter__(self):
        print ("FUNCTION START", self.name, self.num_arguments)
        return (self, [Concrete(i) for i in xrange(self.num_arguments)])

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
