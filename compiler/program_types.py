class Type(object):
    def method_signature(self, name):
        raise KeyError('no such method %s on %s' % (name, self))

    def resolve_type(self, types):
        return self

class Void(Type):
    @property
    def size(self):
        return 0

void = Void()

class Bool(Type):
    @property
    def size(self):
        return 1

    def method_signature(self, name):
        return bool_methods[name]

    def method(self, basic_block, object_variable, name, arguments):
        if name == 'and':
            return basic_block.operation('and', [object_variable] + arguments)
        else:
            raise KeyError('no such method %s on %s' % (name, self))

bool = Bool()

bool_methods = {
    'and': ([bool], bool)
}

class Byte(Type):
    @property
    def size(self):
        return 1

byte = Byte()

class UInt(Type):
    @property
    def size(self):
        return 8

uint = UInt()

class NamedType(Type):
    def __init__(self, name):
        self.name = name

    @property
    def size(self):
        raise Exception()

    def resolve_type(self, types):
        return types[self.name]

class Record(Type):
    def __init__(self, name, attrs, constructors, methods):
        self.name = name
        self.attrs = attrs
        self.constructors = constructors
        self.methods = methods
        self.size = sum([t.size for (_, t) in attrs])

    def method_signature(self, name):
        return self.methods[name]

    def method(self, basic_block, object_variable, name, arguments):
        self.methods[name]
        return basic_block.fun_call('%s#%s' % (self.name, name), [object_variable] + arguments)

class Array(Type):
    def __init__(self, ty, count):
        self.ty = ty
        self.count = count

    @property
    def size(self):
        return self.ty.size * self.count

    def resolve_type(self, types):
        self.ty = self.ty.resolve_type(types)
        return self

    def __eq__(self, other):
        return isinstance(other, Array) and self.ty == other.ty and self.count == other.count

    def __ne__(self, other):
        return not self.__eq__(other)

class Tuple(Type):
    def __init__(self, types):
        self.types = types

    @property
    def size(self):
        return sum([t.size for t in self.types])

    def resolve_type(self, types):
        self.types = [t.resolve_type(types) for t in self.types]
        return self

    def __eq__(self, other):
        return isinstance(other, Tuple) and self.types == other.types

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<Tuple (%s)>' % ', '.join([repr(t) for t in self.types])
