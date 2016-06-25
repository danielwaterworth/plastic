import data
from data import operator

class DHashMap(data.Data):
    def __init__(self, h):
        self.h = h

@operator('hashmap.empty')
def call(self, arguments):
    assert len(arguments) == 0
    return DHashMap({})

@operator('hashmap.set')
def call(self, arguments):
    map, key, value = arguments
    assert isinstance(map, DHashMap)
    assert isinstance(key, data.String)
    updated_map = {}
    updated_map.update(map.h)
    updated_map[key.v] = value
    return DHashMap(updated_map)

@operator('hashmap.get')
def call(self, arguments):
    map, key = arguments
    assert isinstance(map, DHashMap)
    assert isinstance(key, data.String)
    return map.h[key.v]

@operator('hashmap.del')
def call(self, arguments):
    map, key = arguments
    assert isinstance(map, DHashMap)
    assert isinstance(key, data.String)
    updated_map = {}
    updated_map.update(map.h)
    del updated_map[key.v]
    return DHashMap(updated_map)
