import data

class BoolAnd(data.BuiltinOperator):
    def __init__(self):
        self.name = 'and'

    def call(self, arguments):
        a, b = arguments
        assert isinstance(a, data.Bool)
        assert isinstance(b, data.Bool)
        return data.Bool(a.b and b.b)

BoolAnd().register()

class BoolOr(data.BuiltinOperator):
    def __init__(self):
        self.name = 'or'

    def call(self, arguments):
        a, b = arguments
        assert isinstance(a, data.Bool)
        assert isinstance(b, data.Bool)
        return data.Bool(a.b or b.b)

BoolOr().register()

class BoolNot(data.BuiltinOperator):
    def __init__(self):
        self.name = 'not'

    def call(self, arguments):
        assert len(arguments) == 1
        arg = arguments[0]
        assert isinstance(arg, data.Bool)
        return data.Bool(not arg.b)

BoolNot().register()
