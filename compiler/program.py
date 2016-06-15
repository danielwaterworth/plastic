class Decl(object):
    pass

class Function(Decl):
    def __init__(self, name, parameters, return_type, body):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body

    def resolve_types(self, types):
        self.parameters = [(name, param.resolve_type(types)) for name, param in self.parameters]
        self.return_type = self.return_type.resolve_type(types)

    @property
    def parameter_types(self):
        return [param[1] for param in self.parameters]

    @property
    def signature(self):
        return (self.parameter_types, self.return_type)

class Record(Decl):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

class Interface(Decl):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

class Service(Decl):
    def __init__(self, name, dependencies, decls):
        self.name = name
        self.dependencies = dependencies
        self.decls = decls

class Entry(Decl):
    def __init__(self, body):
        self.body = body

class Attr(Decl):
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Constructor(Decl):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def resolve_types(self, types):
        self.parameters = [(name, t.resolve_type(types)) for name, t in self.parameters]

    @property
    def parameter_types(self):
        return [param[1] for param in self.parameters]

class Implements(Decl):
    def __init__(self, interface, decls):
        self.interface = interface
        self.decls = decls

class Private(Decl):
    def __init__(self, decls):
        self.decls = decls

class MethodSignature(object):
    def __init__(self, name, parameters, return_type):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type

    def resolve_types(self, types):
        self.parameters = [param.resolve_type(types) for param in self.parameters]
        self.return_type = self.return_type.resolve_type(types)

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

class ServiceConstructorCall(Expression):
    def __init__(self, service, service_arguments, name, arguments):
        self.service = service
        self.service_arguments = service_arguments
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
