import data
from data import operator

class DList(data.Data):
    def __init__(self, elements):
        self.elements = elements

@operator('list.pack')
def call(self, arguments):
    return [DList(arguments)]

@operator('list.append')
def call(self, arguments):
    list, element = arguments
    if not isinstance(list, DList):
        raise TypeError()
    return [DList(list.elements + [element])]

@operator('list.extend')
def call(self, arguments):
    a, b = arguments
    if not isinstance(a, DList):
        raise TypeError()
    if not isinstance(b, DList):
        raise TypeError()
    return [DList(a.elements + b.elements)]

@operator('list.repeat')
def call(self, arguments):
    element, n = arguments
    if not isinstance(n, data.UInt):
        raise TypeError()
    return [DList([element] * n.n)]

@operator('list.set')
def call(self, arguments):
    list, index, value = arguments
    assert isinstance(index, data.UInt)
    index_n = index.n
    if not isinstance(list, DList):
        raise TypeError()
    if not isinstance(index, data.UInt):
        raise TypeError()
    if index_n < 0 or index_n >= len(list.elements):
        raise IndexError()
    return [DList(list.elements[:index_n] + [value] + list.elements[index_n+1:])]

@operator('list.index')
def call(self, arguments):
    list, index = arguments
    if not isinstance(list, DList):
        raise TypeError()
    if not isinstance(index, data.UInt):
        raise TypeError()
    if index.n < 0 or index.n >= len(list.elements):
        raise IndexError()
    return [list.elements[index.n]]

@operator('list.length')
def call(self, arguments):
    assert len(arguments) == 1
    list = arguments[0]
    assert isinstance(list, DList)
    return [data.UInt(len(list.elements))]

@operator('list.reverse')
def call(self, arguments):
    assert len(arguments) == 1
    l = arguments[0]
    assert isinstance(l, DList)
    l = list(l.elements)
    l.reverse()
    return [DList(l)]
