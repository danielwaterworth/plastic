import data

import operators.int
import operators.uint
import operators.double
import operators.bool
import operators.byte
import operators.char
import operators.bytestring
import operators.string
import operators.list
import operators.hashmap

from rpython.rlib.jit import purefunction

@purefunction
def operator(operator):
    return data.operators[operator]
