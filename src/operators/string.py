import data
import operators.list
from data import operator

@operator('string.length')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.String)
    return [data.UInt(len(x.v))]

@operator('string.concat')
def call(self, arguments):
    x, y = arguments
    assert isinstance(x, data.String)
    assert isinstance(y, data.String)
    return [data.String(x.v + y.v)]

@operator('string.head')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.String)
    assert len(x.v) > 0
    return [data.Char(x.v[0])]

@operator('string.tail')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.String)
    assert len(x.v) > 0
    return [data.String(x.v[1:])]

@operator('string.drop')
def call(self, arguments):
    x, n = arguments
    assert isinstance(x, data.String)
    assert isinstance(n, data.UInt)
    assert len(x.v) >= n.n
    return [data.String(x.v[n.n:])]

@operator('string.take')
def call(self, arguments):
    x, n = arguments
    assert isinstance(x, data.String)
    assert isinstance(n, data.UInt)
    assert len(x.v) >= n.n
    return [data.String(x.v[:n.n])]

@operator('string.eq')
def call(self, arguments):
    x, y = arguments
    assert isinstance(x, data.String)
    assert isinstance(y, data.String)
    return [data.Bool(x.v == y.v)]

@operator('string.encode_utf8')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.String)
    return [data.ByteString(x.v.encode('utf-8'))]

@operator('string.pack')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, operators.list.DList)
    chars = []
    for c in x.elements:
        assert isinstance(c, data.Char)
        chars.append(c.b)
    return [data.String(u''.join(chars))]

@operator('string.unpack')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.String)
    return [operators.list.DList([data.Char(c) for c in x.v])]
