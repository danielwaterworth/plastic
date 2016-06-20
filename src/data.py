class Data(object):
    pass

class UInt(Data):
    def __init__(self, n):
        self.n = n

    def write_out(self, basic_block):
        return basic_block.constant_uint(self.n)

class Bool(Data):
    def __init__(self, b):
        self.b = b

    def write_out(self, basic_block):
        return basic_block.constant_bool(self.b)

class Void(Data):
    def write_out(self, basic_block):
        return basic_block.void()

class Byte(Data):
    def __init__(self, b):
        self.b = b

    def write_out(self, basic_block):
        return basic_block.constant_byte(self.b)

class String(Data):
    def __init__(self, v):
        self.v = v

    def write_out(self, basic_block):
        return basic_block.constant_string(self.v)

class Packed(Data):
    def __init__(self, values):
        self.values = values

def operation(operator, arguments):
    if operator == 'sub':
        a, b = arguments
        return sub(a, b)
    elif operator == 'add':
        a, b = arguments
        return add(a, b)
    elif operator == 'eq':
        a, b = arguments
        return eq(a, b)
    elif operator == 'lt':
        a, b = arguments
        return lt(a, b)
    elif operator == 'and':
        a, b = arguments
        return and_(a, b)
    elif operator == 'pack':
        return Packed(arguments)
    elif operator == 'index':
        a, b = arguments
        assert isinstance(a, Packed)
        assert isinstance(b, UInt)
        return a.values[b.n]
    elif operator == 'string_eq':
        a, b = arguments
        return string_eq(a, b)
    elif operator == 'string_index':
        string, index = arguments
        return string_index(string, index)
    elif operator == 'string_slice':
        string, start, stop = arguments
        return string_slice(string, start, stop)
    elif operator == 'byte_eq':
        a, b = arguments
        return byte_eq(a, b)
    else:
        raise NotImplementedError('operator not implemented: %s' % operator)

def sub(a, b):
    assert isinstance(a, UInt)
    assert isinstance(b, UInt)
    return UInt(a.n - b.n)

def add(a, b):
    assert isinstance(a, UInt)
    assert isinstance(b, UInt)
    return UInt(a.n - b.n)

def lt(a, b):
    assert isinstance(a, UInt)
    assert isinstance(b, UInt)
    return Bool(a.n < b.n)

def and_(a, b):
    assert isinstance(a, Bool)
    assert isinstance(b, Bool)
    return Bool(a.b and b.b)

def eq(a, b):
    assert isinstance(a, UInt)
    assert isinstance(b, UInt)
    return Bool(a.n == b.n)

def string_eq(a, b):
    assert isinstance(a, String)
    assert isinstance(b, String)
    return Bool(a.v == b.v)

def string_index(string, index):
    assert isinstance(string, String)
    assert isinstance(index, UInt)
    assert len(string.v) > index.n
    return Byte(string.v[index.n])

def string_slice(string, start, stop):
    assert isinstance(string, String)
    assert isinstance(start, UInt)
    assert isinstance(stop, UInt)
    raise NotImplementedError()

def byte_eq(a, b):
    assert isinstance(a, Byte)
    assert isinstance(b, Byte)
    return Bool(a.b == b.b)
