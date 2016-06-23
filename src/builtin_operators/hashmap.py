import data

class DHashMap(data.Data):
    def __init__(self, h):
        self.h = h

    def lookup(self, method):
        return methods[method]

context = {}
methods = {}

class Empty(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.hashmap.empty'

    def call(self, arguments):
        assert len(arguments) == 0
        return DHashMap({})

Empty().register()

class Set(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.hashmap.set'

    def call(self, arguments):
        map, key, value = arguments
        assert isinstance(map, DHashMap)
        assert isinstance(key, data.String)
        updated_map = {}
        updated_map.update(map.h)
        updated_map[key.v] = value
        return DHashMap(updated_map)

hashmap_set = Set()
context['vm.hashmap.set'] = hashmap_set
methods['set'] = hashmap_set

class Get(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.hashmap.get'

    def call(self, arguments):
        map, key = arguments
        assert isinstance(map, DHashMap)
        assert isinstance(key, data.String)
        return map.h[key.v]

hashmap_get = Get()
context['vm.hashmap.get'] = hashmap_get
methods['get'] = hashmap_get

class Del(data.BuiltinOperator):
    def __init__(self):
        self.name = 'vm.hashmap.del'

    def call(self, arguments):
        map, key = arguments
        assert isinstance(map, DHashMap)
        assert isinstance(key, data.String)
        updated_map = {}
        updated_map.update(map.h)
        del updated_map[key.v]
        return DHashMap(updated_map)

hashmap_del = Del()
context['vm.hashmap.del'] = hashmap_del
methods['del'] = hashmap_del
