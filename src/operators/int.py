import data
from data import operator

@operator('int.add')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Int(a.n + b.n)

@operator('int.sub')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Int(a.n - b.n)

@operator('int.mul')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Int(a.n * b.n)

@operator('int.div')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Int(a.n / b.n)

@operator('int.gt')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Bool(a.n > b.n)

@operator('int.lt')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Bool(a.n < b.n)

@operator('int.ge')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Bool(a.n >= b.n)

@operator('int.le')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Bool(a.n <= b.n)

@operator('int.eq')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Bool(a.n == b.n)

@operator('int.ne')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Int):
        raise TypeError()
    if not isinstance(b, data.Int):
        raise TypeError()
    return data.Bool(a.n != b.n)

@operator('int.to_string')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    if not isinstance(x, data.Int):
        raise TypeError()
    return data.String(str(x.n).decode('utf-8'))

@operator('int.from_string')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    if not isinstance(x, data.String):
        raise TypeError()
    return data.Int(int(x.v))
