import data
from data import operator

@operator('char.eq')
def call(self, arguments):
    x, y = arguments
    assert isinstance(x, data.Char)
    assert isinstance(y, data.Char)
    return [data.Bool(x.b == y.b)]

@operator('char.to_string')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Char)
    return [data.String(x.b)]

digits = [unicode(i) for i in xrange(10)]
spaces = [u' ', '\r', '\n']
lowers = [unichr(i) for i in xrange(ord('a'), ord('z') + 1)]
uppers = [unichr(i) for i in xrange(ord('A'), ord('Z') + 1)]

@operator('char.is_lower')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Char)
    return [data.Bool(x.b in lowers)]

@operator('char.is_upper')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Char)
    return [data.Bool(x.b in uppers)]

@operator('char.is_digit')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Char)
    return [data.Bool(x.b in digits)]

@operator('char.is_space')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    assert isinstance(x, data.Char)
    return [data.Bool(x.b in spaces)]
