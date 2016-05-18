import struct
import StringIO
import binascii

from bytecode.format import *

class BasicBlockWriter(object):
    def __init__(self, function, writer):
        self.function = function
        self.writer = writer
        self.block_writer = StringIO.StringIO()
        self.terminated = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not value:
            assert self.terminated

    def constant(self, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', CONST))
        self.block_writer.write(struct.pack('>Q', len(value)))
        self.block_writer.write(value)
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

    def ret(self, variable):
        assert not self.terminated
        self.terminated = True
        self.block_writer.write(struct.pack('>B', RET))
        self.block_writer.write(struct.pack('>Q', variable))

    def write_out(self):
        self.writer.write(self.block_writer.getvalue())

class FunctionWriter(object):
    def __init__(self, writer, name, arguments):
        self.writer = writer
        self.name = name
        self.arguments = arguments
        self.basic_blocks = []
        self.next_variable = len(arguments)

    def create_variable(self):
        v = self.next_variable
        self.next_variable += 1
        return v

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if not value:
            name_symbol = self.writer.symbol(self.name)
            self.writer.write(struct.pack('>B', FUNCTION_START))
            self.writer.write(name_symbol)

            self.writer.write(struct.pack('>Q', len(self.arguments)))
            for arg in self.arguments:
                self.writer.write(struct.pack('>Q', arg))

            self.writer.write(struct.pack('>Q', len(self.basic_blocks)))
            for basic_block in self.basic_blocks:
                basic_block.write_out()

    def basic_block(self):
        bb = BasicBlockWriter(self, self.writer)
        self.basic_blocks.append(bb)
        return bb

class ProgramWriter(object):
    def __init__(self, writer):
        self.writer = writer

    def function(self, name, arguments):
        return FunctionWriter(self.writer, name, arguments)

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
