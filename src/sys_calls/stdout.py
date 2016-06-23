import data

class PrintString(data.SysCall):
    def __init__(self):
        self.name = 'print_string'

    def call(self, arguments):
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.String)
        print a.v
        return data.Void()

PrintString().register()

class PrintUInt(data.SysCall):
    def __init__(self):
        self.name = 'print_uint'

    def call(self, arguments):
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.UInt)
        print a.n
        return data.Void()

PrintUInt().register()

class PrintBool(data.SysCall):
    def __init__(self):
        self.name = 'print_bool'

    def call(self, arguments):
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.Bool)
        if a.b:
            print 'True'
        else:
            print 'False'
        return data.Void()

PrintBool().register()

class PrintChar(data.SysCall):
    def __init__(self):
        self.name = 'print_char'

    def call(self, arguments):
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.Char)
        print a.b
        return data.Void()

PrintChar().register()
