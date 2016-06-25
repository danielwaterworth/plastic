import data
from data import operator

@operator('byte.eq')
def call(self, arguments):
    x, y = arguments
    assert isinstance(x, data.Byte)
    assert isinstance(y, data.Byte)
    return data.Bool(x.b == y.b)

@operator('byte.to_bytestring')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Byte)
    return data.ByteString(x.b)

@operator('byte.to_uint')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Byte)
    return data.UInt(ord(x.b[0]))

@operator('byte.from_uint')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.UInt)
    assert x.n < 256
    return data.Byte(chr(x.n))
