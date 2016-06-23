from data import *
import builtin_operators

def operation(operator, arguments):
    if operator in operators:
        return operators[operator].call(arguments)

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
    elif operator == 'bytestring_eq':
        a, b = arguments
        return bytestring_eq(a, b)
    elif operator == 'bytestring_index':
        string, index = arguments
        return bytestring_index(string, index)
    elif operator == 'bytestring_slice':
        string, start, stop = arguments
        return bytestring_slice(string, start, stop)
    elif operator == 'bytestring_length':
        assert len(arguments) == 1
        return bytestring_length(arguments[0])
    elif operator == 'decode_utf8':
        assert len(arguments) == 1
        return decode_utf8(arguments[0])
    elif operator == 'byte_eq':
        a, b = arguments
        return byte_eq(a, b)
    elif operator == 'char_eq':
        a, b = arguments
        return char_eq(a, b)
    elif operator == 'encode_utf8':
        assert len(arguments) == 1
        return encode_utf8(arguments[0])
    elif operator == 'string_head':
        assert len(arguments) == 1
        return string_head(arguments[0])
    elif operator == 'string_drop':
        x, y = arguments
        return string_drop(x, y)
    elif operator == 'string_eq':
        x, y = arguments
        return string_eq(x, y)
    else:
        raise NotImplementedError('operator not implemented: %s' % operator)

def sub(a, b):
    assert isinstance(a, UInt)
    assert isinstance(b, UInt)
    return UInt(a.n - b.n)

def add(a, b):
    assert isinstance(a, UInt)
    assert isinstance(b, UInt)
    return UInt(a.n + b.n)

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

def bytestring_eq(a, b):
    assert isinstance(a, ByteString)
    assert isinstance(b, ByteString)
    return Bool(a.v == b.v)

def bytestring_index(string, index):
    assert isinstance(string, ByteString)
    assert isinstance(index, UInt)
    assert len(string.v) > index.n
    return Byte(string.v[index.n])

def bytestring_slice(string, start, stop):
    assert isinstance(string, ByteString)
    assert isinstance(start, UInt)
    assert isinstance(stop, UInt)
    return ByteString(string.v[start.n:stop.n])

def bytestring_length(string):
    assert isinstance(string, ByteString)
    return UInt(len(string.v))

def decode_utf8(x):
    assert isinstance(x, ByteString)
    return String(x.v.decode('utf-8'))

def byte_eq(a, b):
    assert isinstance(a, Byte)
    assert isinstance(b, Byte)
    return Bool(a.b == b.b)

def char_eq(a, b):
    assert isinstance(a, Char)
    assert isinstance(b, Char)
    return Bool(a.b == b.b)

def encode_utf8(x):
    assert isinstance(x, String)
    return ByteString(x.v.encode('utf-8'))

def string_head(x):
    assert isinstance(x, String)
    assert len(x.v) > 0
    return Char(x.v[0])

def string_drop(x, n):
    assert isinstance(x, String)
    assert isinstance(n, UInt)
    assert len(x.v) >= n.n
    return String(x.v[n.n:])

def string_eq(x, y):
    assert isinstance(x, String)
    assert isinstance(y, String)
    return Bool(x.v == y.v)
