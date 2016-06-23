import builtin_operators.uintops
import builtin_operators.boolops
import builtin_operators.list
import builtin_operators.hashmap
import builtin_operators.ffi

context = {}

context.update(builtin_operators.ffi.context)

for operator in context.itervalues():
    operator.register()
