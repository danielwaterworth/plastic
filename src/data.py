from rpython.rlib.objectmodel import compute_hash
from rpython.rlib.rstruct.runpack import runpack
from rpython.rlib.rarithmetic import intmask, r_ulonglong
import hashlib

operators = {}
sys_calls = {}

def pack_uint(n):
    output = []
    for i in xrange(8):
        output.append(chr(n & 0xff))
        n = n >> 8
    output.reverse()
    return ''.join(output)

def pack_int(n):
    n = n & r_ulonglong(0xffffffffffffffffL)
    return pack_uint(n)

def pack_uint32(n):
    output = []
    for i in xrange(4):
        output.append(chr(n & 0xff))
        n = n >> 8
    output.reverse()
    return ''.join(output)

class BuiltinOperator(object):
    def register(self):
        operators[self.name] = self

class ExposeConstant(BuiltinOperator):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def call(self, arguments):
        assert len(arguments) == 0
        return [self.value]

def expose_constant(name, value):
    ExposeConstant(name, value).register()

class SysCall(object):
    def register(self):
        sys_calls[self.name] = self

def sys_call(name):
    def decorator(f):
        class DecoratedSysCall(SysCall):
            def __init__(self):
                self.name = name

            call = f
        DecoratedSysCall().register()
    return decorator

def operator(name):
    def decorator(f):
        class DecoratedOperator(BuiltinOperator):
            def __init__(self):
                self.name = name

            call = f
        DecoratedOperator().register()
    return decorator

type_by_id = {}
class Data(object):
    @classmethod
    def register(cls):
        i = hashlib.sha256("%s::%s" % (cls.__module__, cls.__name__)).digest()[:8]
        assert not i in type_by_id
        type_by_id[i] = cls
        cls.type_id = i

    def debug(self):
        return u"(unknown)"

    def copy(self):
        return self

    def persist(self, fd):
        raise NotImplementedError()

    def eq(self, other):
        raise NotImplementedError()

    def hash(self):
        raise NotImplementedError()

def load(fd):
    id = fd.read(8)
    return type_by_id[id].load(fd)

def register_all():
    for cls in Data.__subclasses__():
        cls.register()

class Int(Data):
    def __init__(self, n):
        self.n = n

    def write_out(self, basic_block):
        return basic_block.constant_int(self.n)

    def eq(self, other):
        return isinstance(other, Int) and self.n == other.n

    def hash(self):
        return compute_hash(self.n)

class UInt(Data):
    def __init__(self, n):
        self.n = n

    def persist(self, fd):
        fd.write(self.type_id)
        fd.write(pack_uint(self.n))

    @staticmethod
    def load(fd):
        n = runpack('>Q', fd.read(8))
        return UInt(n)

    def write_out(self, basic_block):
        return basic_block.constant_uint(self.n)

    def __repr__(self):
        return repr(self.n)

    def eq(self, other):
        return isinstance(other, UInt) and self.n == other.n

    def hash(self):
        return compute_hash(self.n)

class Double(Data):
    def __init__(self, d):
        self.d = d

    def write_out(self, basic_block):
        return basic_block.constant_double(self.d)

class Bool(Data):
    def __init__(self, b):
        self.b = b

    def persist(self, fd):
        fd.write(self.type_id)
        fd.write('\1' if self.b else '\0')

    @staticmethod
    def load(fd):
        n = runpack('>Q', fd.read(8))
        return Bool(fd.read(1) != '\0')

    def write_out(self, basic_block):
        return basic_block.constant_bool(self.b)

    def __repr__(self):
        return repr(self.b)

    def eq(self, other):
        return isinstance(other, Bool) and self.b == other.b

    def hash(self):
        return compute_hash(self.b)

class Invalid(Data):
    def write_out(self, basic_block):
        raise Exception()

    def persist(self, fd):
        raise Exception()

    @staticmethod
    def load(fd):
        raise Exception()

    def __repr__(self):
        return 'invalid'

class Void(Data):
    def write_out(self, basic_block):
        return basic_block.void()

    def persist(self, fd):
        fd.write(self.type_id)

    @staticmethod
    def load(fd):
        return Void()

    def __repr__(self):
        return 'void'

class Byte(Data):
    def __init__(self, b):
        self.b = b

    def persist(self, fd):
        fd.write(self.type_id)
        fd.write(self.b)

    @staticmethod
    def load(fd):
        return Byte(fd.read(1))

    def write_out(self, basic_block):
        return basic_block.constant_byte(self.b)

    def __repr__(self):
        return repr(self.b)

    def eq(self, other):
        return isinstance(other, Byte) and self.b == other.b

    def hash(self):
        return compute_hash(self.b)

class Char(Data):
    def __init__(self, b):
        self.b = b

    def persist(self, fd):
        fd.write(self.type_id)
        fd.write(pack_uint32(ord(self.b)))

    @staticmethod
    def load(fd):
        return Char(unichr(runpack('>I', fd.read(4))))

    def write_out(self, basic_block):
        return basic_block.constant_char(self.b)

    def __repr__(self):
        return repr(self.b)

    def eq(self, other):
        return isinstance(other, Char) and self.b == other.b

    def hash(self):
        return compute_hash(self.b)

class ByteString(Data):
    def __init__(self, v):
        assert not v is None
        self.v = v

    def debug(self):
        return u'b\"%s\"' % self.v.decode('utf-8')

    def persist(self, fd):
        fd.write(self.type_id)
        fd.write(pack_uint(len(self.v)))
        fd.write(self.v)

    @staticmethod
    def load(fd):
        n = intmask(runpack('>Q', fd.read(8)))
        return ByteString(fd.read(n))

    def write_out(self, basic_block):
        return basic_block.constant_bytestring(self.v)

    def __repr__(self):
        return repr(self.v)

    def eq(self, other):
        return isinstance(other, ByteString) and self.v == other.v

    def hash(self):
        return compute_hash(self.v)

class String(Data):
    def __init__(self, v):
        self.v = v

    def debug(self):
        return u'\"%s\"' % self.v

    def write_out(self, basic_block):
        return basic_block.constant_string(self.v)

    def persist(self, fd):
        fd.write(self.type_id)
        v = self.v.encode('utf-8')
        fd.write(pack_uint(len(v)))
        fd.write(v)

    @staticmethod
    def load(fd):
        n = intmask(runpack('>Q', fd.read(8)))
        return String(fd.read(n).decode('utf-8'))

    def __repr__(self):
        return repr(self.v)

    def eq(self, other):
        return isinstance(other, String) and self.v == other.v

    def hash(self):
        return compute_hash(self.v)
