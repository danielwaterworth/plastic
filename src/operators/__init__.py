import operators.uint
import operators.bool
import operators.string
import operators.list
import operators.hashmap

from data import *

def operation(operator, arguments):
    if operator in operators:
        return operators[operator].call(arguments)
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
    else:
        raise NotImplementedError('operator not implemented: %s' % operator)

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
