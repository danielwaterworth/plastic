import struct
import data

class Decl(object):
    pass

class Coroutine(Decl):
    def __init__(self, name, parameters, receive_type, yield_type, body):
        self.name = name
        self.parameters = parameters
        self.receive_type = receive_type
        self.yield_type = yield_type
        self.body = body

    def resolve_types(self, types):
        self.parameters = [(name, param.resolve_type(types)) for name, param in self.parameters]
        self.receive_type = self.receive_type.resolve_type(types)
        self.yield_type = self.yield_type.resolve_type(types)

    @property
    def num_parameters(self):
        return len(self.parameters)

    @property
    def parameter_types(self):
        return [param[1] for param in self.parameters]

    @property
    def parameter_names(self):
        return [param[0] for param in self.parameters]

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
    def num_parameters(self):
        return len(self.parameters)

    @property
    def parameter_types(self):
        return [param[1] for param in self.parameters]

    @property
    def signature(self):
        return (self.parameter_types, self.return_type)

    @property
    def parameter_names(self):
        return [param[0] for param in self.parameters]

class Record(Decl):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

class Enum(Decl):
    def __init__(self, name, constructors):
        self.name = name
        self.constructors = constructors

class Interface(Decl):
    def __init__(self, name, decls):
        self.name = name
        self.decls = decls

class Service(Decl):
    def __init__(self, name, dependencies, decls):
        self.name = name
        self.dependencies = dependencies
        self.decls = decls

    @property
    def dependency_names(self):
        return [name for name, _ in self.dependencies]

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
    def num_parameters(self):
        return len(self.parameters)

    @property
    def parameter_types(self):
        return [param[1] for param in self.parameters]

    @property
    def parameter_names(self):
        return [param[0] for param in self.parameters]

class Implements(Decl):
    def __init__(self, interface, decls):
        self.interface = interface
        self.decls = decls

class Private(Decl):
    def __init__(self, decls):
        self.decls = decls

class EnumConstructor(object):
    def __init__(self, name, types):
        self.name = name
        self.types = types

    def resolve_types(self, types):
        self.types = [t.resolve_type(types) for t in self.types]

class MethodSignature(object):
    def __init__(self, name, parameters, return_type):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type

    def resolve_types(self, types):
        self.parameters = [param.resolve_type(types) for param in self.parameters]
        self.return_type = self.return_type.resolve_type(types)

class CodeBlock(object):
    def __init__(self, statements, terminator=None):
        self.statements = statements
        self.terminator = terminator

    def evaluate(self, context):
        for statement in self.statements:
            statement.evaluate(context)

        if isinstance(self.terminator, Return):
            return self.terminator.expression.evaluate(context)
        else:
            raise NotImplementedError()

class Statement(object):
    pass

class Assignment(Statement):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

    def evaluate(self, context):
        value = self.expression.evaluate(context)
        context.add(self.name, value)

class AttrStore(Statement):
    def __init__(self, attr, value):
        self.attr = attr
        self.value = value

    def evaluate(self, context):
        value = self.value.evaluate(context)
        context.attr_add(self.attr, value)

class TupleDestructure(Statement):
    def __init__(self, names, expression):
        self.names = names
        self.expression = expression

class Conditional(Statement):
    def __init__(self, expression, true_block, false_block):
        self.expression = expression
        self.true_block = true_block
        self.false_block = false_block

class While(Statement):
    def __init__(self, body, expression):
        self.expression = expression
        self.body = body

class Match(Statement):
    def __init__(self, expression, clauses):
        self.expression = expression
        self.clauses = clauses

class Clause(object):
    def __init__(self, name, parameters, block):
        self.name = name
        self.parameters = parameters
        self.block = block

class Expression(Statement):
    pass

class Variable(Expression):
    def __init__(self, name):
        self.name = name

    def evaluate(self, context):
        return context.lookup(self.name)

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

    def evaluate(self, context):
        service_arguments = [arg.evaluate(context) for arg in self.service_arguments]
        arguments = [arg.evaluate(context) for arg in self.arguments]
        return context.service(self.service, service_arguments, self.name, arguments)

class TupleConstructor(Expression):
    def __init__(self, values):
        self.values = values

class AttrLoad(Expression):
    def __init__(self, attr):
        self.attr = attr

class Yield(Expression):
    def __init__(self, value):
        self.value = value

class Run(Expression):
    def __init__(self, coroutine):
        self.coroutine = coroutine

class Resume(Expression):
    def __init__(self, coroutine, value):
        self.coroutine = coroutine
        self.value = value

class IsDone(Expression):
    def __init__(self, coroutine):
        self.coroutine = coroutine

class ByteLiteral(Expression):
    def __init__(self, b):
        self.b = b

    def evaluate(self, context):
        return data.Byte(self.b)

class NumberLiteral(Expression):
    def __init__(self, n):
        self.n = n

    def evaluate(self, context):
        return data.UInt(self.n)

class BoolLiteral(Expression):
    def __init__(self, b):
        self.b = b

    def evaluate(self, context):
        return data.Bool(self.b)

class VoidLiteral(Expression):
    def evaluate(self, context):
        return data.Void()

class StringLiteral(Expression):
    def __init__(self, v):
        self.v = v

    def evaluate(self, context):
        return data.ByteString(v)

class Terminator(object):
    pass

class Return(Terminator):
    def __init__(self, expression):
        self.expression = expression

class Throw(Terminator):
    pass
