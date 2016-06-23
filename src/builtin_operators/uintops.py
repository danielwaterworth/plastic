import data

context = {}

class IntAdd(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.add'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n + b.n)

context['vm.intops.add'] = IntAdd()

class IntSub(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.sub'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, data.UInt):
            raise TypeError()
        if not isinstance(b, data.UInt):
            raise TypeError()
        return data.UInt(a.n - b.n)

context['vm.intops.sub'] = IntSub()

class IntMul(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.mul'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.mul'] = IntMul()

class IntDiv(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.div'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.div'] = IntDiv()

class IntGt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.gt'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.gt'] = IntGt()

class IntLt(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.lt'

    def call(self, arguments):
        a, b = arguments
        assert isinstance(a, data.UInt)
        assert isinstance(b, data.UInt)
        return data.Bool(a.n < b.n)

context['vm.intops.lt'] = IntLt()

class IntGe(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.ge'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.ge'] = IntGe()

class IntLe(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.le'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.le'] = IntLe()

class IntEq(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.eq'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.eq'] = IntEq()

class IntNe(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.ne'

    def call(self, arguments):
        a, b = arguments
        raise NotImplementedError()

context['vm.intops.ne'] = IntNe()

class ToString(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.intops.to_string'

    def call(self, arguments):
        assert len(arguments) == 1
        x = arguments[0]
        if not isinstance(x, data.UInt):
            raise TypeError()
        return data.String(str(x.n).decode('utf-8'))

context['vm.intops.to_string'] = ToString()
