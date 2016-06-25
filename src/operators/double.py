import data
from data import operator

@operator('double.add')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Double(a.d + b.d)

@operator('double.sub')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Double(a.d - b.d)

@operator('double.mul')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Double(a.d * b.d)

@operator('double.div')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Double(a.d / b.d)

@operator('double.gt')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Bool(a.d > b.d)

@operator('double.lt')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Bool(a.d < b.d)

@operator('double.ge')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Bool(a.d >= b.d)

@operator('double.le')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Bool(a.d <= b.d)

@operator('double.eq')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Bool(a.d == b.d)

@operator('double.ne')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, data.Double):
        raise TypeError()
    if not isinstance(b, data.Double):
        raise TypeError()
    return data.Bool(a.d != b.d)

@operator('double.to_string')
def call(self, arguments):
    assert len(arguments) == 1
    x = arguments[0]
    if not isinstance(x, data.Double):
        raise TypeError()
    return data.String(str(x.d).decode('utf-8'))
