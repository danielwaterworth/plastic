import data

class Head(data.BuiltinOperator):
    def __init__(self):
        self.name = 'string.head'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.String)
        assert len(x.v) > 0
        return data.Char(x.v[0])

Head().register()

class Drop(data.BuiltinOperator):
    def __init__(self):
        self.name = 'string.drop'

    def call(self, arguments):
        x, n = arguments
        assert isinstance(x, data.String)
        assert isinstance(n, data.UInt)
        assert len(x.v) >= n.n
        return data.String(x.v[n.n:])

Drop().register()

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'string.eq'

    def call(self, arguments):
        x, y = arguments
        assert isinstance(x, data.String)
        assert isinstance(y, data.String)
        return data.Bool(x.v == y.v)

Eq().register()

class EncodeUtf8(data.BuiltinOperator):
    def __init__(self):
        self.name = 'string.encode_utf8'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.String)
        return data.ByteString(x.v.encode('utf-8'))

EncodeUtf8().register()
