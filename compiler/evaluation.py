import collections
import struct

class ServiceInstantiation(object):
    def __init__(self, service, service_arguments, name, arguments):
        self.service = service
        self.service_arguments = service_arguments
        self.name = name
        self.arguments = arguments

    def interface_variable(self, basic_block):
        service_type = basic_block.constant(struct.pack('>Q', self.service_type_id))
        service_id = basic_block.constant(struct.pack('>Q', self.service_id))
        return basic_block.operation('pack', [service_type, service_id])

    def service_variable(self, basic_block):
        return basic_block.constant(struct.pack('>Q', self.service_id))

class EvaluationContext(object):
    def __init__(self, variables):
        self.variables = {}
        self.services = []

    def lookup(self, name):
        return self.variables[name]

    def add(self, name, variable):
        self.variables[name] = variable

    def service(self, service, service_arguments, name, arguments):
        instantiation = ServiceInstantiation(service, service_arguments, name, arguments)
        self.services.append(instantiation)
        return instantiation
