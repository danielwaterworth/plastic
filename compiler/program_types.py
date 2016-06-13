class Type(object):
    def method_signature(self, name):
        raise KeyError('no such method %s on %s' % (name, self))

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

class UInt(Type):
    @property
    def size(self):
        return 8

uint = UInt()

bool_methods = {
    'and': ([bool], bool)
}

class NamedType(Type):
    def __init__(self, name):
        self.name = name

    @property
    def size(self):
        raise Exception()

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
