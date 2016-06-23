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
