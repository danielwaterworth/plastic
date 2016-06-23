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
