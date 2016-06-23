import data

import operators.int
import operators.uint
import operators.bool
import operators.byte
import operators.char
import operators.bytestring
import operators.string
import operators.list
import operators.hashmap

def operation(operator, arguments):
    return data.operators[operator].call(arguments)
