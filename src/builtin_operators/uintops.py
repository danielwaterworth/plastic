import data

class IntAdd(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.add'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n + b.n)

IntAdd().register()

class IntSub(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.sub'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n - b.n)

IntSub().register()

class IntMul(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.mul'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

IntMul().register()

class IntDiv(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.div'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

IntDiv().register()

class IntGt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.gt'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

IntGt().register()

class IntLt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.lt'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n < b.n)

IntLt().register()

class IntGe(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.ge'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

IntGe().register()

class IntLe(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.le'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

IntLe().register()

class IntEq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.eq'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.Bool(a.n == b.n)

IntEq().register()

class IntNe(data.BuiltinOperator):
    def __init__(self):
        self.name = 'uint.ne'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        raise NotImplementedError()

IntNe().register()

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
