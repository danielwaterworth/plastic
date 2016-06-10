import struct
import StringIO
import binascii

from bytecode.format import *

class Variable(object):
    pass

class Concrete(Variable):
    def __init__(self, n):
        self.n = n

    def write(self, block_writer):
        block_writer.write(struct.pack('>Q', self.n))

class Forward(Variable):
    def __init__(self):
        self.places = []
        self.n = 0
        self.instantiated = False

    def write(self, block_writer):
        if not self.instantiated:
            self.places.append((block_writer, block_writer.tell()))
        block_writer.write(struct.pack('>Q', self.n))

    def assign(self, var):
        assert isinstance(var, Concrete)
        self.instantiated = True
        self.n = var.n
        for block_writer, pos in self.places:
            before = block_writer.tell()
            block_writer.seek(pos)
            block_writer.write(struct.pack('>Q', self.n))
            block_writer.seek(before)
        del self.places[:]

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

    def phi(self, inputs):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', PHI))
        self.block_writer.write(struct.pack('>Q', len(inputs)))

        for block, var in inputs:
            self.block_writer.write(struct.pack('>Q', block))
            var.write(self.block_writer)
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
            arg.write(self.block_writer)
        return self.function.create_variable()

    def sys_call(self, function, arguments):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', SYS_CALL))
        self.block_writer.write(self.writer.symbol(function))

        self.block_writer.write(struct.pack('>Q', len(arguments)))
        for arg in arguments:
            arg.write(self.block_writer)
        return self.function.create_variable()

    def fun_call(self, function, arguments):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', FUN_CALL))
        self.block_writer.write(self.writer.symbol(function))

        self.block_writer.write(struct.pack('>Q', len(arguments)))
        for arg in arguments:
            arg.write(self.block_writer)
        return self.function.create_variable()

    def load(self, address):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', LOAD))
        address.write(self.block_writer)
        return self.function.create_variable()

    def store(self, address, value):
        assert not self.terminated
        self.block_writer.write(struct.pack('>B', STORE))
        address.write(self.block_writer)
        value.write(self.block_writer)
        return self.function.create_variable()

    def terminator(self):
        assert not self.terminated
        self.terminated = True

    def ret(self, variable):
        self.terminator()
        self.block_writer.write(struct.pack('>B', RET))
        variable.write(self.block_writer)

    def goto(self, block):
        self.terminator()
        self.block_writer.write(struct.pack('>B', GOTO))
        self.block_writer.write(struct.pack('>Q', block))

    def conditional(self, variable, true_block, false_block):
        self.terminator()
        self.block_writer.write(struct.pack('>B', CONDITIONAL))
        variable.write(self.block_writer)
        self.block_writer.write(struct.pack('>Q', true_block))
        self.block_writer.write(struct.pack('>Q', false_block))

    def forward(self):
        return Forward()

    def write_out(self):
        self.writer.write(self.block_writer.getvalue())

class FunctionWriter(object):
    def __init__(self, writer, name, num_arguments):
        self.writer = writer
        self.name = name
        self.basic_blocks = []
        self.num_arguments = num_arguments
        self.next_variable = num_arguments

    def create_variable(self):
        v = self.next_variable
        self.next_variable += 1
        return Concrete(v)

    def __enter__(self):
        return (self, [Concrete(i) for i in xrange(self.num_arguments)])

    def __exit__(self, type, value, traceback):
        if not value:
            name_symbol = self.writer.symbol(self.name)
            self.writer.write(struct.pack('>B', FUNCTION_START))
            self.writer.write(name_symbol)

            self.writer.write(struct.pack('>Q', self.num_arguments))

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

    def function(self, name, num_arguments):
        return FunctionWriter(self.writer, name, num_arguments)

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
