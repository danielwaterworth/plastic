import data
from data import operator

@operator('and')
def call(self, arguments):
    a, b = arguments
    assert isinstance(a, data.Bool)
    assert isinstance(b, data.Bool)
    return [data.Bool(a.b and b.b)]

@operator('or')
def call(self, arguments):
    a, b = arguments
    assert isinstance(a, data.Bool)
    assert isinstance(b, data.Bool)
    return [data.Bool(a.b or b.b)]

@operator('not')
def call(self, arguments):
    assert len(arguments) == 1
    arg = arguments[0]
    assert isinstance(arg, data.Bool)
    return [data.Bool(not arg.b)]
