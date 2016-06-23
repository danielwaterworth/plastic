operators = {}

class BuiltinOperator(object):
    def call(self, arguments):
        raise NotImplementedError()

    def register(self):
        operators[self.name] = self

class Data(object):
    pass

class UInt(Data):
    def __init__(self, n):
        self.n = n

    def write_out(self, basic_block):
        return basic_block.constant_uint(self.n)

class Bool(Data):
    def __init__(self, b):
        self.b = b

    def write_out(self, basic_block):
        return basic_block.constant_bool(self.b)

class Void(Data):
    def write_out(self, basic_block):
        return basic_block.void()

class Byte(Data):
    def __init__(self, b):
        self.b = b

    def write_out(self, basic_block):
        return basic_block.constant_byte(self.b)

class Char(Data):
    def __init__(self, b):
        self.b = b

    def write_out(self, basic_block):
        return basic_block.constant_char(self.b)

class ByteString(Data):
    def __init__(self, v):
        self.v = v

    def write_out(self, basic_block):
        return basic_block.constant_bytestring(self.v)

class String(Data):
    def __init__(self, v):
        self.v = v

    def write_out(self, basic_block):
        return basic_block.constant_string(self.v)
