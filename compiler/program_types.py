class Type(object):
    def method_signature(self, name):
        raise KeyError('no such method %s' % name)

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
            raise KeyError('no such method %s' % name)

bool = Bool()

class UInt(Type):
    @property
    def size(self):
        return 8

uint = UInt()

bool_methods = {
    'and': ([bool], bool)
}
