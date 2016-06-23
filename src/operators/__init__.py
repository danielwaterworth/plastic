import operators.uint
import operators.bool
import operators.bytestring
import operators.string
import operators.list
import operators.hashmap

from data import *

def operation(operator, arguments):
    if operator in operators:
        return operators[operator].call(arguments)
    elif operator == 'byte_eq':
        a, b = arguments
        return byte_eq(a, b)
    elif operator == 'char_eq':
        a, b = arguments
        return char_eq(a, b)
    else:
        raise NotImplementedError('operator not implemented: %s' % operator)

def byte_eq(a, b):
    assert isinstance(a, Byte)
    assert isinstance(b, Byte)
    return Bool(a.b == b.b)

def char_eq(a, b):
    assert isinstance(a, Char)
    assert isinstance(b, Char)
    return Bool(a.b == b.b)
