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
NEW_COROUTINE = 6
LOAD = 7
STORE = 8
RUN_COROUTINE = 9
YIELD = 10
RESUME = 11

RET = 129
GOTO = 130
CONDITIONAL = 131
CATCH_FIRE_AND_DIE = 132
