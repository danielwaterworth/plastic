import data

context = {}

class BoolAnd(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.boolops.and'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.boolops.and'] = BoolAnd()

class BoolOr(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.boolops.or'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.boolops.or'] = BoolOr()

class BoolNot(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.boolops.not'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()
