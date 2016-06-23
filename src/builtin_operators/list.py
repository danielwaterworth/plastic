import data

class DList(data.Data):
    def __init__(self, elements):
        self.elements = elements

    def lookup(self, method):
        return methods[method]

context = {}
methods = {}

class Append(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.list.append'

    def call(self, arguments):
        list, element = arguments
        if not isinstance(list, DList):
            raise TypeError()
        return DList(list.elements + [element])

list_append = Append()
context['vm.list.append'] = list_append
methods['append'] = list_append

class Extend(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.list.extend'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, DList):
            raise TypeError()
        if not isinstance(b, DList):
            raise TypeError()
        return DList(a.elements + b.elements)

list_extend = Extend()
context['vm.list.extend'] = list_extend
methods['extend'] = list_extend

class Repeat(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.list.repeat'

    def call(self, arguments):
        element, n = arguments
        if not isinstance(n, data.UInt):
            raise TypeError()
        return DList([element] * n.n)

context['vm.list.repeat'] = Repeat()

class Set(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.list.set'

    def call(self, arguments):
        list, index, value = arguments
        index_n = index.n
        if not isinstance(list, DList):
            raise TypeError()
        if not isinstance(index, data.UInt):
            raise TypeError()
        if index_n < 0 or index_n >= len(list.elements):
            raise IndexError()
        return DList(list.elements[:index_n] + [value] + list.elements[index_n+1:])

list_set = Set()
context['vm.list.set'] = list_set
methods['set'] = list_set

class Get(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.list.get'

    def call(self, arguments):
        list, index = arguments
        if not isinstance(list, DList):
            raise TypeError()
        if not isinstance(index, data.UInt):
            raise TypeError()
        if index.n < 0 or index.n >= len(list.elements):
            raise IndexError()
        return list.elements[index.n]

list_get = Get()
context['vm.list.get'] = list_get
methods['get'] = list_get