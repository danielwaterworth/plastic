import collections
import program

class ServiceInstantiation(object):
    def __init__(self, service, service_arguments, attrs):
        self.service = service
        self.service_arguments = service_arguments
        self.attrs = attrs

    def interface_variable(self, basic_block):
        service_type = basic_block.constant_uint(self.service_type_id)
        service_id = basic_block.constant_uint(self.service_id)
        return basic_block.operation('pack', [service_type, service_id])

    def service_variable(self, basic_block):
        return basic_block.constant_uint(self.service_id)

class EvaluationContext(object):
    def __init__(self, service_constructors, variables):
        self.service_constructors = service_constructors
        self.variables = {}
        self.services = []
        self.attrs = {}

    def lookup(self, name):
        return self.variables[name]

    def add(self, name, value):
        self.variables[name] = value

    def attr_add(self, name, value):
        self.attrs[name] = value

    def service(self, service, service_arguments, name, arguments):
        constructor = self.service_constructors[(service, name)]
        variables = dict(zip(constructor.parameter_names, arguments))

        new_context = EvaluationContext(self.service_constructors, variables)
        for statement in constructor.body.statements:
            statement.evaluate(new_context)

        instantiation = ServiceInstantiation(service, service_arguments, new_context.attrs)
        self.services.append(instantiation)
        return instantiation

def evaluate_entry_block(modules, entry_module):
    service_constructors = {}

    entry_block = None
    for decl in modules[entry_module].decls:
        if isinstance(decl, program.Entry):
            assert not entry_block
            entry_block = decl.body

    for module_name, module in modules.iteritems():
        for decl in module.decls:
            if isinstance(decl, program.Service):
                for service_decl in decl.decls:
                    if isinstance(service_decl, program.Constructor):
                        service_constructors[(decl.name, service_decl.name)] = service_decl

    assert entry_block
    context = EvaluationContext(service_constructors, {})
    return entry_block.evaluate(context)
