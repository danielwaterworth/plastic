from rpython.rlib.rstruct.runpack import runpack

from bytecode_format import *

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
                length = runpack('>Q', fd.read(8))
                value = fd.read(length)
                symbols.append(symbols)
            elif type == FUNCTION_START:
                name_n = runpack('>Q', fd.read(8))
                name = symbols[name_n]
                arguments_n = runpack('>Q', fd.read(8))
                arguments = []
                for i in xrange(arguments_n):
                    arguments.append(runpack('>Q', fd.read(8)))

                with program_receiver.function(name, arguments) as function_receiver:
                    basic_block_n = runpack('>Q', fd.read(8))
                    for i in xrange(basic_block_n):
                        with function_receiver.basic_block() as basic_block_receiver:
                            while True:
                                instruction_type = runpack('>B', fd.read(1))
                                if instruction_type == CONST:
                                    length = runpack('>Q', fd.read(8))
                                    basic_block_receiver.constant(fd.read(length))
                                elif instruction_type == SYSCALL:
                                    function_name_n = runpack('>Q', fd.read(8))
                                    function_name = symbols[function_name_n]
                                    arguments_n = runpack('>Q', fd.read(8))
                                    arguments = []
                                    for i in xrange(arguments_n):
                                        arguments.append(runpack('>Q', fd.read(8)))
                                    basic_block_receiver.syscall(function_name, arguments)
                                elif instruction_type == RET:
                                    variable = runpack('>Q', fd.read(8))
                                    basic_block_receiver.ret(variable)
                                    break
                                else:
                                    raise NotImplementedError()
            else:
                raise NotImplementedError()
