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

class ToByteString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'byte.to_bytestring'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.Byte)
        return data.ByteString(x.b)

ToByteString().register()

class ToUInt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'byte.to_uint'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.Byte)
        return data.UInt(ord(x.b[0]))

ToUInt().register()

class FromUInt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'byte.from_uint'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        assert isinstance(x, data.UInt)
        assert x.n < 256
        return data.Byte(chr(x.n))

FromUInt().register()
