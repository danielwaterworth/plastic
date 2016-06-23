import data

class DHashMap(data.Data):
    def __init__(self, h):
        self.h = h

class Empty(data.BuiltinOperator):
    def __init__(self):
        self.name = 'hashmap.empty'

    def call(self, arguments):
        assert len(arguments) == 0
        return DHashMap({})

Empty().register()

class Set(data.BuiltinOperator):
    def __init__(self):
        self.name = 'hashmap.set'

    def call(self, arguments):
        map, key, value = arguments
        assert isinstance(map, DHashMap)
        assert isinstance(key, data.String)
        updated_map = {}
        updated_map.update(map.h)
        updated_map[key.v] = value
        return DHashMap(updated_map)

Set().register()

class Get(data.BuiltinOperator):
    def __init__(self):
        self.name = 'hashmap.get'

    def call(self, arguments):
        map, key = arguments
        assert isinstance(map, DHashMap)
        assert isinstance(key, data.String)
        return map.h[key.v]

Get().register()

class Del(data.BuiltinOperator):
    def __init__(self):
        self.name = 'hashmap.del'

    def call(self, arguments):
        map, key = arguments
        assert isinstance(map, DHashMap)
        assert isinstance(key, data.String)
        updated_map = {}
        updated_map.update(map.h)
        del updated_map[key.v]
        return DHashMap(updated_map)

Del().register()
