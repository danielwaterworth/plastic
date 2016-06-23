import data

class Add(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.add'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Double(a.d + b.d)

Add().register()

class Sub(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.sub'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Double(a.d - b.d)

Sub().register()

class Mul(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.mul'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Double(a.d * b.d)

Mul().register()

class Div(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.div'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Double(a.d / b.d)

Div().register()

class Gt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.gt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Bool(a.d > b.d)

Gt().register()

class Lt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.lt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Bool(a.d < b.d)

Lt().register()

class Ge(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.ge'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Bool(a.d >= b.d)

Ge().register()

class Le(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.le'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Bool(a.d <= b.d)

Le().register()

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.eq'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Bool(a.d == b.d)

Eq().register()

class Ne(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.ne'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.Double):
            raise TypeError()
        if not isinstance(b, data.Double):
            raise TypeError()
        return data.Bool(a.d != b.d)

Ne().register()

class ToString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'double.to_string'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        if not isinstance(x, data.Double):
            raise TypeError()
        return data.String(str(x.d).decode('utf-8'))

ToString().register()
