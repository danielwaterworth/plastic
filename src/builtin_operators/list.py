import data

class DList(data.Data):
    def __init__(self, elements):
        self.elements = elements

class Pack(data.BuiltinOperator):
    def __init__(self):
        self.name = 'list.pack'

    def call(self, arguments):
        return DList(arguments)

Pack().register()

class Append(data.BuiltinOperator):
    def __init__(self):
        self.name = 'list.append'

    def call(self, arguments):
        list, element = arguments
        if not isinstance(list, DList):
            raise TypeError()
        return DList(list.elements + [element])

Append().register()

class Extend(data.BuiltinOperator):
    def __init__(self):
        self.name = 'list.extend'

    def call(self, arguments):
        a, b = arguments
        if not isinstance(a, DList):
            raise TypeError()
        if not isinstance(b, DList):
            raise TypeError()
        return DList(a.elements + b.elements)

Extend().register()

class Repeat(data.BuiltinOperator):
    def __init__(self):
        self.name = 'list.repeat'

    def call(self, arguments):
        element, n = arguments
        if not isinstance(n, data.UInt):
            raise TypeError()
        return DList([element] * n.n)

Repeat().register()

class Set(data.BuiltinOperator):
    def __init__(self):
        self.name = 'list.set'

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

Set().register()

class Index(data.BuiltinOperator):
    def __init__(self):
        self.name = 'list.index'

    def call(self, arguments):
        list, index = arguments
        if not isinstance(list, DList):
            raise TypeError()
        if not isinstance(index, data.UInt):
            raise TypeError()
        if index.n < 0 or index.n >= len(list.elements):
            raise IndexError()
        return list.elements[index.n]

Index().register()
