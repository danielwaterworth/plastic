import data

class Head(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.head'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.ByteString)
        assert len(x.v) > 0
        return data.Byte(x.v[0])

Head().register()

class Drop(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.drop'

    def call(self, arguments):
        x, n = arguments
        assert isinstance(x, data.ByteString)
        assert isinstance(n, data.UInt)
        assert len(x.v) >= n.n
        return data.ByteString(x.v[n.n:])

Drop().register()

class Eq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.eq'

    def call(self, arguments):
        x, y = arguments
        assert isinstance(x, data.ByteString)
        assert isinstance(y, data.ByteString)
        return data.Bool(x.v == y.v)

Eq().register()

class DecodeUtf8(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.decode_utf8'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.ByteString)
        return data.String(x.v.decode('utf-8'))

DecodeUtf8().register()

class Index(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.index'

    def call(self, arguments):
        string, index = arguments
        assert isinstance(string, data.ByteString)
        assert isinstance(index, data.UInt)
        assert len(string.v) > index.n
        return data.Byte(string.v[index.n])

Index().register()

class Slice(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.slice'

    def bytestring_slice(self, arguments):
        string, start, stop = arguments
        assert isinstance(string, data.ByteString)
        assert isinstance(start, data.UInt)
        assert isinstance(stop, data.UInt)
        return data.ByteString(string.v[start.n:stop.n])

Slice().register()

class Length(data.BuiltinOperator):
    def __init__(self):
        self.name = 'bytestring.length'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.ByteString)
        return data.UInt(len(x.v))

Length().register()
