import data

class Add(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.add'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Int(a.n + b.n)

Add().register()

class Sub(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.sub'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Int(a.n - b.n)

Sub().register()

class Mul(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.mul'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Int(a.n * b.n)

Mul().register()

class Div(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.div'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Int(a.n / b.n)

Div().register()

class Gt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.gt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Bool(a.n > b.n)

Gt().register()

class Lt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.lt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Bool(a.n < b.n)

Lt().register()

class Ge(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.ge'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Bool(a.n >= b.n)

Ge().register()

class Le(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.le'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Bool(a.n <= b.n)

Le().register()

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.eq'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Bool(a.n == b.n)

Eq().register()

class Ne(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.ne'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Int):
            raise TypeError()
        if not isinstance(b, data.Int):
            raise TypeError()
        return data.Bool(a.n != b.n)

Ne().register()

class ToString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.to_string'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        if not isinstance(x, data.Int):
            raise TypeError()
        return data.String(str(x.n).decode('utf-8'))

ToString().register()

class FromString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'int.from_string'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        if not isinstance(x, data.String):
            raise TypeError()
        return data.Int(int(x.v))

FromString().register()
