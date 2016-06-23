import data

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'char.eq'

    def call(self, arguments):
        x, y = arguments
        assert isinstance(x, data.Char)
        assert isinstance(y, data.Char)
        return data.Bool(x.b == y.b)

Eq().register()

class ToString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'char.to_string'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.Char)
        return data.String(x.b)

ToString().register()
