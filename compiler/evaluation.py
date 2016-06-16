import collections

class ServiceInstantiation(object):
    def __init__(self, service, service_arguments, name, arguments):
        self.service = service
        self.service_arguments = service_arguments
        self.name = name
        self.arguments = arguments

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
