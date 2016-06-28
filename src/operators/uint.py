from rpython.rlib.rstruct.runpack import runpack
import data
from data import operator

@operator('uint.add')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.UInt(a.n + b.n)]

@operator('uint.sub')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.UInt(a.n - b.n)]

@operator('uint.mul')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.UInt(a.n * b.n)]

@operator('uint.div')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.UInt(a.n / b.n)]

@operator('uint.gt')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.Bool(a.n > b.n)]

@operator('uint.lt')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.Bool(a.n < b.n)]

@operator('uint.ge')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.Bool(a.n >= b.n)]

@operator('uint.le')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.Bool(a.n <= b.n)]

@operator('uint.eq')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.Bool(a.n == b.n)]

@operator('uint.ne')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.UInt):
        raise TypeError()
    if not isinstance(b, data.UInt):
        raise TypeError()
    return [data.Bool(a.n != b.n)]

@operator('uint.to_string')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    if not isinstance(x, data.UInt):
        raise TypeError()
    return [data.String(str(x.n).decode('utf-8'))]

@operator('uint.from_string')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    if not isinstance(x, data.String):
        raise TypeError()
    n = 0
    for c in x.v:
        n *= 10
        c = ord(c)
        assert c >= ord('0') and c <= ord('9')
        c = c - ord('0')
        assert c >= 0
        n += c
    return [data.UInt(n)]

@operator('unpack_uint')
def call(self, arguments):
    assert len(arguments) == 1
    b = arguments[0]
    assert isinstance(b, data.ByteString)
    assert len(b.v) == 8
    return [data.UInt(runpack('>Q', b.v))]

