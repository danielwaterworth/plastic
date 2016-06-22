class ModuleInterface(object):
    def __init__(self, name, imports):
        self.name = name
        self.imports = imports
        self.signatures = {}
        self.types = {}
        self.interface_types = {}
        self.services = {}
