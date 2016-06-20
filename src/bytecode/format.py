from rpython.rlib.rstruct.runpack import runpack
from rpython.rlib.rarithmetic import r_ulonglong, r_int, intmask

MAGIC_START = r_ulonglong(17810926409145293181)

# Top level
SYMBOL = 1
FUNCTION_START = 2

# Instructions
PHI = 1

VOID = 8
CONST_UINT = 9
CONST_BOOL = 10
CONST_BYTE = 11
CONST_BYTESTRING = 12
CONST_STRING = 13

OPERATION = 32
SYS_CALL = 33
FUN_CALL = 34
NEW_COROUTINE = 35

LOAD = 64
STORE = 65

RUN_COROUTINE = 96
YIELD = 97
RESUME = 98

RET = 129
GOTO = 130
CONDITIONAL = 131
CATCH_FIRE_AND_DIE = 132
