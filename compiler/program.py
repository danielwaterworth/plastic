class Function(object):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

class CodeBlock(object):
    def __init__(self, statements, ret=None):
        self.statements = statements
        self.ret = ret

class Statement(object):
    pass

class Assignment(Statement):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

class FunctionCallStatement(Statement):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class SysCallStatement(Statement):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class Store(Statement):
    def __init__(self, address, value):
        self.address = address
        self.value = value

class Conditional(Statement):
    def __init__(self, variable, true_block, false_block):
        self.variable = variable
        self.true_block = true_block
        self.false_block = false_block

class While(Statement):
    def __init__(self, body, variable):
        self.variable = variable
        self.body = body

class Expression(object):
    pass

class BinOp(Expression):
    def __init__(self, lhs, rhs, operator):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

class SysCallExpression(Expression):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class FunctionCallExpression(Expression):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class Load(Expression):
    def __init__(self, address):
        self.address = address

class NumberLiteral(Expression):
    def __init__(self, n):
        self.n = n

class BoolLiteral(Expression):
    def __init__(self, b):
        self.b = b

class Return(object):
    def __init__(self, variable):
        self.variable = variable
