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

    def constant(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST))
        self.block_writer.write(struct.pack('>Q', len(value)))
        self.block_writer.write(value)
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

    def load(self, address, size):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', LOAD))
        self.block_writer.write(struct.pack('>Q', address))
        self.block_writer.write(struct.pack('>Q', size))
        return self.function.create_variable()

    def store(self, address, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', STORE))
        self.block_writer.write(struct.pack('>Q', address))
        self.block_writer.write(struct.pack('>Q', value))
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

    def ret(self, variable):
        self.terminator()
        self.block_writer.write(struct.pack('>B', RET))
        self.block_writer.write(struct.pack('>Q', variable))

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

    def write_out(self):
        self.writer.write(self.block_writer.getvalue())

class FunctionWriter(object):
    def __init__(self, writer, name, argument_sizes, return_size):
        self.writer = writer
        self.name = name
        self.basic_blocks = []
        self.argument_sizes = argument_sizes
        self.return_size = return_size
        self.next_variable = len(argument_sizes)

    def create_variable(self):
        v = self.next_variable
        self.next_variable += 1
        return v

    def __enter__(self):
        return (self, [i for i in xrange(len(self.argument_sizes))])

    def __exit__(self, type, value, traceback):
        if not value:
            name_symbol = self.writer.symbol(self.name)
            self.writer.write(struct.pack('>B', FUNCTION_START))
            self.writer.write(name_symbol)

            self.writer.write(struct.pack('>Q', len(self.argument_sizes)))
            for size in self.argument_sizes:
                self.writer.write(struct.pack('>Q', size))

            self.writer.write(struct.pack('>Q', self.return_size))

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

    def function(self, name, argument_sizes, return_size):
        return FunctionWriter(self.writer, name, argument_sizes, return_size)

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
