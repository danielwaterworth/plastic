from rpython.rlib.rstruct.runpack import runpack
from rpython.rlib.rarithmetic import r_longlong, r_ulonglong, r_int, intmask

from bytecode.format import *

def read_bytecode(fd, receiver):
    magic_start = fd.read(8)
    assert runpack('>Q', magic_start) == MAGIC_START
    symbols = []

    with receiver as program_receiver:
        while True:
            type_bytes = fd.read(1)
            if len(type_bytes) == 0:
                break
            type = runpack('>B', type_bytes)

            if type == SYMBOL:
                length = intmask(runpack('>Q', fd.read(8)))
                value = fd.read(length)
                symbols.append(value)
            elif type == FUNCTION_START:
                name_n = intmask(runpack('>Q', fd.read(8)))
                name = symbols[name_n]
                arguments_n = intmask(runpack('>Q', fd.read(8)))
                return_n = intmask(runpack('>Q', fd.read(8)))

                with program_receiver.function(name, arguments_n, return_n) as (function_receiver, _):
                    basic_block_n = intmask(runpack('>Q', fd.read(8)))
                    for i in xrange(basic_block_n):
                        with function_receiver.basic_block() as basic_block_receiver:
                            while True:
                                instruction_type = runpack('>B', fd.read(1))
                                if instruction_type == PHI:
                                    length = intmask(runpack('>Q', fd.read(8)))
                                    inputs = []
                                    for i in xrange(length):
                                        block = runpack('>Q', fd.read(8))
                                        var = runpack('>Q', fd.read(8))
                                        inputs.append((block, var))
                                    basic_block_receiver.phi(inputs)
                                elif instruction_type == COPY:
                                    basic_block_receiver.copy()
                                elif instruction_type == MOVE:
                                    variable = runpack('>Q', fd.read(8))
                                    basic_block_receiver.move(variable)
                                elif instruction_type == UNPACK:
                                    basic_block_receiver.unpack()
                                elif instruction_type == CONST_BYTE:
                                    basic_block_receiver.constant_byte(fd.read(1))
                                elif instruction_type == CONST_CHAR:
                                    basic_block_receiver.constant_char(unichr(runpack('>I', fd.read(4))))
                                elif instruction_type == CONST_BYTESTRING:
                                    length = intmask(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.constant_bytestring(fd.read(length))
                                elif instruction_type == CONST_STRING:
                                    length = intmask(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.constant_string(fd.read(length).decode('utf-8'))
                                elif instruction_type == CONST_BOOL:
                                    basic_block_receiver.constant_bool(fd.read(1) != '\0')
                                elif instruction_type == CONST_INT:
                                    basic_block_receiver.constant_int(runpack('>q', fd.read(8)))
                                elif instruction_type == CONST_UINT:
                                    basic_block_receiver.constant_uint(runpack('>Q', fd.read(8)))
                                elif instruction_type == CONST_DOUBLE:
                                    basic_block_receiver.constant_double(runpack('>d', fd.read(8)))
                                elif instruction_type == VOID:
                                    basic_block_receiver.void()
                                elif instruction_type == OPERATION:
                                    operator_n = intmask(runpack('>Q', fd.read(8)))
                                    operator = symbols[operator_n]
                                    arguments_n = intmask(runpack('>Q', fd.read(8)))
                                    arguments = []
                                    for i in xrange(arguments_n):
                                        arguments.append(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.operation(operator, arguments)
                                elif instruction_type == FUN_CALL:
                                    function_name_n = intmask(runpack('>Q', fd.read(8)))
                                    function_name = symbols[function_name_n]
                                    arguments_n = intmask(runpack('>Q', fd.read(8)))
                                    arguments = []
                                    for i in xrange(arguments_n):
                                        arguments.append(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.fun_call(function_name, arguments)
                                elif instruction_type == SYS_CALL:
                                    function_name_n = intmask(runpack('>Q', fd.read(8)))
                                    function_name = symbols[function_name_n]
                                    arguments_n = intmask(runpack('>Q', fd.read(8)))
                                    arguments = []
                                    for i in xrange(arguments_n):
                                        arguments.append(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.sys_call(function_name, arguments)
                                elif instruction_type == NEW_COROUTINE:
                                    function_name_n = intmask(runpack('>Q', fd.read(8)))
                                    function_name = symbols[function_name_n]
                                    arguments_n = intmask(runpack('>Q', fd.read(8)))
                                    arguments = []
                                    for i in xrange(arguments_n):
                                        arguments.append(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.new_coroutine(function_name, arguments)
                                elif instruction_type == DEBUG:
                                    value = runpack('>Q', fd.read(8))
                                    basic_block_receiver.debug(value)
                                elif instruction_type == LOAD:
                                    address = runpack('>Q', fd.read(8))
                                    basic_block_receiver.load(address)
                                elif instruction_type == STORE:
                                    address = runpack('>Q', fd.read(8))
                                    variable = runpack('>Q', fd.read(8))
                                    basic_block_receiver.store(address, variable)
                                elif instruction_type == GET:
                                    basic_block_receiver.get()
                                elif instruction_type == PUT:
                                    variable = runpack('>Q', fd.read(8))
                                    basic_block_receiver.put(variable)
                                elif instruction_type == RUN_COROUTINE:
                                    coroutine = runpack('>Q', fd.read(8))
                                    basic_block_receiver.run_coroutine(coroutine)
                                elif instruction_type == YIELD:
                                    value = runpack('>Q', fd.read(8))
                                    basic_block_receiver.yield_(value)
                                elif instruction_type == RESUME:
                                    coroutine = runpack('>Q', fd.read(8))
                                    value = runpack('>Q', fd.read(8))
                                    basic_block_receiver.resume(coroutine, value)
                                elif instruction_type == RET:
                                    variables = [runpack('>Q', fd.read(8)) for i in xrange(return_n)]
                                    basic_block_receiver.ret_multiple(variables)
                                    break
                                elif instruction_type == GOTO:
                                    block = runpack('>Q', fd.read(8))
                                    basic_block_receiver.goto(block)
                                    break
                                elif instruction_type == CONDITIONAL:
                                    variable = runpack('>Q', fd.read(8))
                                    true_block = runpack('>Q', fd.read(8))
                                    false_block = runpack('>Q', fd.read(8))
                                    basic_block_receiver.conditional(variable, true_block, false_block)
                                    break
                                elif instruction_type == CATCH_FIRE_AND_DIE:
                                    basic_block_receiver.catch_fire_and_die()
                                    break
                                elif instruction_type == THROW:
                                    exception = runpack('>Q', fd.read(8))
                                    basic_block_receiver.throw(exception)
                                    break
                                else:
                                    raise NotImplementedError("unknown instruction type: %d" % instruction_type)
            else:
                raise NotImplementedError()
