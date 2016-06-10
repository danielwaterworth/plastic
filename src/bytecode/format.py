from rpython.rlib.rstruct.runpack import runpack
from rpython.rlib.rarithmetic import r_ulonglong, r_int, intmask

MAGIC_START = r_ulonglong(17810926409145293181)

# Top level
SYMBOL = 1
FUNCTION_START = 2

# Instructions
PHI = 1
CONST = 2
OPERATION = 3
SYS_CALL = 4
FUN_CALL = 5
LOAD = 6
STORE = 7

RET = 129
GOTO = 130
CONDITIONAL = 131
