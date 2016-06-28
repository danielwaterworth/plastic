import struct
import StringIO
import binascii

from bytecode.format import *

class BasicBlockWriter(object):
    def __init__(self, function, writer, index):
        self.function = function
        self.writer = writer
        self.block_writer = StringIO.StringIO()
        self.terminated = False
        self.index = index

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not value:
            assert self.terminated

    def phi(self, inputs):
        assert isinstance(inputs, list)
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', PHI))
        self.block_writer.write(struct.pack('>Q', len(inputs)))

        for block, var in inputs:
            self.block_writer.write(struct.pack('>Q', block))
            self.block_writer.write(struct.pack('>Q', var))
        return self.function.create_variable()

    def copy(self):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', COPY))
        return self.function.create_variable()

    def move(self, variable):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', MOVE))
        self.block_writer.write(struct.pack('>Q', variable))
        return self.function.create_variable()

    def constant_bool(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST_BOOL))
        self.block_writer.write('\1' if value else '\0')
        return self.function.create_variable()

    def constant_byte(self, value):
        assert not self.terminated
        assert len(value) == 1
        self.block_writer.write(struct.pack('>B', CONST_BYTE))
        self.block_writer.write(value)
        return self.function.create_variable()

    def constant_char(self, value):
        assert not self.terminated
        assert len(value) == 1
        self.block_writer.write(struct.pack('>B', CONST_CHAR))
        self.block_writer.write(struct.pack('>I', ord(value)))
        return self.function.create_variable()

    def constant_bytestring(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST_BYTESTRING))
        self.block_writer.write(struct.pack('>Q', len(value)))
        self.block_writer.write(value)
        return self.function.create_variable()

    def constant_string(self, value):
        assert not self.terminated
        bytes = value.encode('utf-8')
        self.block_writer.write(struct.pack('>B', CONST_STRING))
        self.block_writer.write(struct.pack('>Q', len(bytes)))
        self.block_writer.write(bytes)
        return self.function.create_variable()

    def constant_int(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST_UINT))
        self.block_writer.write(struct.pack('>q', value))
        return self.function.create_variable()

    def constant_uint(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST_UINT))
        self.block_writer.write(struct.pack('>Q', value))
        return self.function.create_variable()

    def constant_double(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST_DOUBLE))
        self.block_writer.write(struct.pack('>d', value))
        return self.function.create_variable()

    def void(self):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', VOID))
        return self.function.create_variable()

    def operation(self, operator, arguments):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', OPERATION))
        self.block_writer.write(self.writer.symbol(operator))

        self.block_writer.write(struct.pack('>Q', len(arguments)))
        for arg in arguments:
            self.block_writer.write(struct.pack('>Q', arg))
        return self.function.create_variable()

    def sys_call(self, function, arguments):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', SYS_CALL))
        self.block_writer.write(self.writer.symbol(function))

        self.block_writer.write(struct.pack('>Q', len(arguments)))
        for arg in arguments:
            self.block_writer.write(struct.pack('>Q', arg))
        return self.function.create_variable()

    def fun_call(self, function, arguments):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', FUN_CALL))
        self.block_writer.write(self.writer.symbol(function))

        self.block_writer.write(struct.pack('>Q', len(arguments)))
        for arg in arguments:
            self.block_writer.write(struct.pack('>Q', arg))
        return self.function.create_variable()

    def new_coroutine(self, function, arguments):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', NEW_COROUTINE))
        self.block_writer.write(self.writer.symbol(function))

        self.block_writer.write(struct.pack('>Q', len(arguments)))
        for arg in arguments:
            self.block_writer.write(struct.pack('>Q', arg))
        return self.function.create_variable()

    def debug(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', DEBUG))
        self.block_writer.write(struct.pack('>Q', value))
        return self.function.create_variable()

    def load(self, address):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', LOAD))
        self.block_writer.write(struct.pack('>Q', address))
        return self.function.create_variable()

    def store(self, address, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', STORE))
        self.block_writer.write(struct.pack('>Q', address))
        self.block_writer.write(struct.pack('>Q', value))
        return self.function.create_variable()

    def get(self):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', GET))
        return self.function.create_variable()

    def put(self, variable):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', PUT))
        self.block_writer.write(struct.pack('>Q', variable))
        return self.function.create_variable()

    def run_coroutine(self, coroutine):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', RUN_COROUTINE))
        self.block_writer.write(struct.pack('>Q', coroutine))
        return self.function.create_variable()

    def yield_(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', YIELD))
        self.block_writer.write(struct.pack('>Q', value))
        return self.function.create_variable()

    def resume(self, coroutine, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', RESUME))
        self.block_writer.write(struct.pack('>Q', coroutine))
        self.block_writer.write(struct.pack('>Q', value))
        return self.function.create_variable()

    def terminator(self):
        assert not self.terminated
        self.terminated = True

    def ret_multiple(self, variables):
        self.terminator()
        assert len(variables) == self.function.num_return_values
        self.block_writer.write(struct.pack('>B', RET))
        for variable in variables:
            self.block_writer.write(struct.pack('>Q', variable))

    def ret(self, variable):
        return self.ret_multiple([variable])

    def goto(self, block):
        self.terminator()
        self.block_writer.write(struct.pack('>B', GOTO))
        self.block_writer.write(struct.pack('>Q', block))

    def conditional(self, variable, true_block, false_block):
        self.terminator()
        self.block_writer.write(struct.pack('>B', CONDITIONAL))
        self.block_writer.write(struct.pack('>Q', variable))
        self.block_writer.write(struct.pack('>Q', true_block))
        self.block_writer.write(struct.pack('>Q', false_block))

    def catch_fire_and_die(self):
        self.terminator()
        self.block_writer.write(struct.pack('>B', CATCH_FIRE_AND_DIE))

    def throw(self, exception):
        self.terminator()
        self.block_writer.write(struct.pack('>B', THROW))
        self.block_writer.write(struct.pack('>Q', exception))

    def write_out(self):
        self.writer.write(self.block_writer.getvalue())

class FunctionWriter(object):
    def __init__(self, writer, name, num_arguments, num_return_values):
        self.writer = writer
        self.name = name
        self.basic_blocks = []
        self.num_arguments = num_arguments
        self.num_return_values = num_return_values
        self.next_variable = num_arguments

    def create_variable(self):
        v = self.next_variable
        self.next_variable += 1
        return v

    def __enter__(self):
        return (self, [i for i in xrange(self.num_arguments)])

    def __exit__(self, type, value, traceback):
        if not value:
            name_symbol = self.writer.symbol(self.name)
            self.writer.write(struct.pack('>B', FUNCTION_START))
            self.writer.write(name_symbol)

            self.writer.write(struct.pack('>Q', self.num_arguments))
            self.writer.write(struct.pack('>Q', self.num_return_values))

            self.writer.write(struct.pack('>Q', len(self.basic_blocks)))
            for basic_block in self.basic_blocks:
                basic_block.write_out()

    def basic_block(self):
        bb = BasicBlockWriter(self, self.writer, len(self.basic_blocks))
        self.basic_blocks.append(bb)
        return bb

class ProgramWriter(object):
    def __init__(self, writer):
        self.writer = writer

    def function(self, name, num_arguments, num_return_values=1):
        return FunctionWriter(self.writer, name, num_arguments, num_return_values)

class BytecodeWriter(object):
    def __init__(self, fd):
        self.started = False
        self.fd = fd
        self.symbols = {}

        self.write(struct.pack('>Q', MAGIC_START))

    def write(self, bytes):
        self.fd.write(bytes)

    def symbol(self, name):
        if name in self.symbols:
            return self.symbols[name]
        self.write(struct.pack('>B', SYMBOL))
        self.write(struct.pack('>Q', len(name)))
        self.write(name)
        n = struct.pack('>Q', len(self.symbols))
        self.symbols[name] = n
        return n

    def __enter__(self):
        assert not self.started
        self.started = True
        return ProgramWriter(self)

    def __exit__(self, type, value, traceback):
        pass
