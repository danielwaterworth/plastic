from rpython.rlib.objectmodel import r_dict
import data
from data import operator

def data_eq(a, b):
    return a.eq(b)

def data_hash(a):
    return a.hash()

def empty():
    return r_dict(data_eq, data_hash)

class DHashMap(data.Data):
    def __init__(self, h):
        self.h = h

@operator('hashmap.empty')
def call(self, arguments):
    assert len(arguments) == 0
    return [DHashMap(empty())]

@operator('hashmap.set')
def call(self, arguments):
    map, key, value = arguments
    assert isinstance(map, DHashMap)
    updated_map = empty()
    updated_map.update(map.h)
    updated_map[key] = value
    return [DHashMap(updated_map)]

@operator('hashmap.get')
def call(self, arguments):
    map, key = arguments
    assert isinstance(map, DHashMap)
    return [map.h[key]]

@operator('hashmap.del')
def call(self, arguments):
    map, key = arguments
    assert isinstance(map, DHashMap)
    updated_map = empty()
    updated_map.update(map.h)
    del updated_map[key]
    return [DHashMap(updated_map)]

