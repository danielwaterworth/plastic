class Type(object):
    def method_signature(self, name):
        raise KeyError('no such method %s on %s' % (name, self))

    def resolve_type(self, modules, types):
        return self

    def is_subtype_of(self, other):
        return self == other

class Primitive(Type):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def method_signature(self, name):
        return self.methods[name][0]

    def method(self, basic_block, object_variable, name, arguments):
        operator = self.methods[name][1]
        return basic_block.operation(operator, [object_variable] + arguments)

    def match(self, _, other):
        assert isinstance(other, Primitive) and self.name == other.name

    def template(self, _):
        return self

    def __repr__(self):
        return self.name

void = Primitive('void', {})

bool_methods = {}
bool = Primitive('bool', bool_methods)

byte_methods = {}
byte = Primitive('byte', byte_methods)

bytestring_methods = {}
bytestring = Primitive('bytestring', bytestring_methods)

char_methods = {}
char = Primitive('char', char_methods)

string_methods = {}
string = Primitive('string', string_methods)

uint_methods = {}
uint = Primitive('uint', uint_methods)

socket = Primitive('socket', {})

class NamedType(Type):
    def __init__(self, module, name):
        self.module = module
        self.name = name

    def resolve_type(self, modules, types):
        if self.module:
            return modules[self.module].types[self.name]
        else:
            return types[self.name]

    def resolve_interface(self, modules, interface_types):
        if self.module:
            return modules[self.module].interface_types[self.name]
        else:
            return interface_types[self.name]

class Variable(Type):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name

    def match(self, quantified, other):
        if self.name in quantified:
            assert quantified[self.name] == other
        else:
            quantified[self.name] = other

    def template(self, quantified):
        return quantified[self.name]

class Instantiation(Type):
    def __init__(self, constructor, types):
        self.constructor = constructor
        self.types = types

    def resolve_type(self, modules, types):
        self.types = [t.resolve_type(modules, types) for t in self.types]
        return self

    def __eq__(self, other):
        return isinstance(other, Instantiation) and self.constructor == other.constructor and self.types == other.types

    def __ne__(self, other):
        return not self.__eq__(other)

    def match(self, quantified, other):
        assert isinstance(other, Instantiation)
        assert self.constructor == other.constructor
        assert len(self.types) == len(other.types)
        for a, b in zip(self.types, other.types):
            a.match(quantified, b)

    def template(self, quantified):
        return Instantiation(self.constructor, [t.template(quantified) for t in self.types])

    def __repr__(self):
        if self.constructor.name == 'Tuple':
            return '(%s)' % ', '.join([repr(t) for t in self.types])
        else:
            return '<%s (%s)>' % (self.constructor.name, ', '.join([repr(t) for t in self.types]))

    def method_signature(self, name):
        return self.constructor.constructor_method_signature(self.types, name)

    def method(self, basic_block, object_variable, name, arguments):
        return self.constructor.method(basic_block, object_variable, name, arguments)

class TypeConstructor(object):
    pass

tuple = TypeConstructor()
tuple.name = 'Tuple'

def tuple_type(*arguments):
    return Instantiation(tuple, arguments)

coroutine = TypeConstructor()
coroutine.name = 'Coroutine'

def coroutine_type(receive_type, yield_type):
    return Instantiation(coroutine, [receive_type, yield_type])

class Enum(TypeConstructor):
    def __init__(self, name, constructors):
        self.name = name
        self.constructors = constructors

class Record(TypeConstructor):
    def __init__(self, name, attrs, constructor_signatures, methods):
        self.name = name
        self.attrs = attrs
        self.constructor_signatures = constructor_signatures
        self.methods = methods

    def constructor_method_signature(self, types, name):
        return self.methods[name]

    def method(self, basic_block, object_variable, name, arguments):
        self.methods[name]
        return basic_block.fun_call('%s#%s' % (self.name, name), [object_variable] + arguments)

class Interface(Type):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def method_signature(self, name):
        return self.methods[name]

    def method(self, basic_block, object_variable, name, arguments):
        return basic_block.fun_call("%s#%s" % (self.name, name), [object_variable] + arguments)

    def __repr__(self):
        return "<Interface %s>" % self.name

# Type used for self in a service context
class PrivateService(Type):
    def __init__(self, name, private_methods):
        self.name = name
        self.private_methods = private_methods

    def method_signature(self, name):
        return self.private_methods[name]

    def method(self, basic_block, object_variable, name, arguments):
        return basic_block.fun_call("%s#%s" % (self.name, name), [object_variable] + arguments)

class Service(Type):
    def __init__(self, name, dependencies, attrs, constructor_signatures, interfaces):
        self.name = name
        self.dependencies = dependencies
        self.attrs = attrs
        self.constructor_signatures = constructor_signatures
        self.interfaces = interfaces

    @property
    def all_attrs(self):
        all_attrs = dict(self.attrs)
        all_attrs.update(dict(self.dependencies))
        return all_attrs

    @property
    def dependency_types(self):
        return [t for _, t in self.dependencies]

    def is_subtype_of(self, other):
        if isinstance(other, Interface):
            return other in self.interfaces
        return self == other

    def __repr__(self):
        return "<Service %s>" % self.name

uint_methods.update({
    'to_string': (([], string), 'uint.to_string')
})

byte_methods.update({
    'to_bytestring': (([], bytestring), 'byte.to_bytestring'),
    'to_uint': (([], uint), 'byte.to_uint'),
})

char_methods.update({
    'to_string': (([], string), 'char.to_string')
})

bytestring_methods.update({
    'drop': (([uint], bytestring), 'bytestring.drop'),
    'take': (([uint], bytestring), 'bytestring.take'),
    'index': (([uint], byte), 'bytestring.index'),
    'slice': (([uint, uint], bytestring), 'bytestring.slice'),
    'length': (([], uint), 'bytestring.length'),
    'decode_utf8': (([], string), 'bytestring.decode_utf8')
})

string_methods.update({
    'head': (([], char), 'string.head'),
    'drop': (([uint], string), 'string.drop'),
    'encode_utf8': (([], bytestring), 'string.encode_utf8')
})
