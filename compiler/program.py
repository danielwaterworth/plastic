class TopLevelDecl(object):
    pass

class Function(TopLevelDecl):
    def __init__(self, name, parameters, return_type, body):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

class Record(TopLevelDecl):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

class RecordDecl(object):
    pass

class Attr(RecordDecl):
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Constructor(RecordDecl):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

class Method(RecordDecl):
    def __init__(self, name, parameters, return_type, body):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
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

class Store(Statement):
    def __init__(self, address, value):
        self.address = address
        self.value = value

class AttrStore(Statement):
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value

class Conditional(Statement):
    def __init__(self, expression, true_block, false_block):
        self.expression = expression
        self.true_block = true_block
        self.false_block = false_block

class While(Statement):
    def __init__(self, body, expression):
        self.expression = expression
        self.body = body

class Expression(Statement):
    pass

class Variable(Expression):
    def __init__(self, name):
        self.name = name

class BinOp(Expression):
    def __init__(self, lhs, rhs, operator):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

class SysCall(Expression):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class FunctionCall(Expression):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MethodCall(Expression):
    def __init__(self, obj, name, arguments):
        self.obj = obj
        self.name = name
        self.arguments = arguments

class ConstructorCall(Expression):
    def __init__(self, ty, name, arguments):
        self.ty = ty
        self.name = name
        self.arguments = arguments

class Load(Expression):
    def __init__(self, address):
        self.address = address

class AttrLoad(Expression):
    def __init__(self, attr):
        self.attr = attr

class NumberLiteral(Expression):
    def __init__(self, n):
        self.n = n

class BoolLiteral(Expression):
    def __init__(self, b):
        self.b = b

class Return(object):
    def __init__(self, expression):
        self.expression = expression
