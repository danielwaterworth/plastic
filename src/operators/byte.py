import data

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'byte.eq'

    def call(self, arguments):
        x, y = arguments
        assert isinstance(x, data.Byte)
        assert isinstance(y, data.Byte)
        return data.Bool(x.b == y.b)

Eq().register()
