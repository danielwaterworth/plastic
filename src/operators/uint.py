import data

class Add(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.add'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n + b.n)

Add().register()

class Sub(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.sub'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n - b.n)

Sub().register()

class Mul(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.mul'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n * b.n)

Mul().register()

class Div(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.div'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n / b.n)

Div().register()

class Gt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.gt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n > b.n)

Gt().register()

class Lt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.lt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n < b.n)

Lt().register()

class Ge(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.ge'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n >= b.n)

Ge().register()

class Le(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.le'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n <= b.n)

Le().register()

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.eq'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n == b.n)

Eq().register()

class Ne(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.ne'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n != b.n)

Ne().register()

class ToString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.to_string'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        if not isinstance(x, data.UInt):
            raise TypeError()
        return data.String(str(x.n).decode('utf-8'))

ToString().register()

class FromString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.from_string'

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
        return data.UInt(n)

FromString().register()
