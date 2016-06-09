from rpython.rlib.rstruct.runpack import runpack
from rpython.rlib.rarithmetic import r_ulonglong, r_int, intmask

MAGIC_START = r_ulonglong(17810926409145293181)

# Top level
SYMBOL = 1
FUNCTION_START = 2

# Instructions
PHI = 1
CONST = 2
SYS_CALL = 3
FUN_CALL = 4
LOAD = 5
STORE = 6

RET = 129
GOTO = 130
CONDITIONAL = 131
