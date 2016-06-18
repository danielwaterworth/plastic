import collections
import itertools
import struct
import program
import program_types

class GenerationContext(object):
    def __init__(self, function_writer, basic_block, variables):
        self.function_writer = function_writer
        self.basic_block = basic_block
        self.variables = variables

    def add(self, name, variable):
        self.variables[name] = variable

    def lookup(self, name):
        return self.variables[name]

    def new_context(self, basic_block):
        raise NotImplementedError()

    def attr_add(self, name, value):
        raise NotImplementedError()

    def attr_lookup(self, name):
        raise NotImplementedError()

class FunctionContext(GenerationContext):
    def new_context(self, basic_block):
        return FunctionContext(self.function_writer, basic_block, dict(self.variables))

class RecordContext(GenerationContext):
    def new_context(self, basic_block):
        return RecordContext(self.function_writer, basic_block, dict(self.variables))

    def attr_add(self, name, value):
        self.add('@%s' % name, value)

    def attr_lookup(self, name):
        return self.lookup('@%s' % name)

class ServiceContext(GenerationContext):
    def __init__(self, name, dependencies, attrs, self_variable, function_writer, basic_block, variables):
        self.name = name
        self.dependencies = dependencies
        self.attrs = attrs
        self.self_variable = self_variable
        self.function_writer = function_writer
        self.basic_block = basic_block
        self.variables = variables

    def new_context(self, basic_block):
        return ServiceContext(
                    self.name,
                    self.dependencies,
                    self.attrs,
                    self.self_variable,
                    self.function_writer,
                    basic_block,
                    dict(self.variables)
                )

    def attr_lookup(self, name):
        if name in self.dependencies:
            return self.basic_block.fun_call('%s^%s' % (self.name, name), [self.self_variable])
        elif name in self.attrs:
            attr = self.attrs[name]
            offset = self.basic_block.fun_call('%s^%s' % (self.name, name), [self.self_variable])
            return self.basic_block.load(offset, attr.size)
        else:
            raise NotImplementedError()

    def attr_add(self, name, value):
        offset = self.basic_block.fun_call('%s^%s' % (self.name, name), [self.self_variable])
        self.basic_block.store(offset, value)

operators = {
    '<': 'lt',
    '>': 'gt',
    '<=': 'le',
    '>=': 'ge',
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '==': 'eq',
    '!=': 'ne'
}

def generate_expression(context, expression):
    if isinstance(expression, program.Variable):
        return context.lookup(expression.name)
    elif isinstance(expression, program.ByteLiteral):
        return context.basic_block.constant(expression.b)
    elif isinstance(expression, program.NumberLiteral):
        return context.basic_block.constant(struct.pack('>Q', expression.n))
    elif isinstance(expression, program.BoolLiteral):
        return context.basic_block.constant(struct.pack('>B', 1 if expression.b else 0))
    elif isinstance(expression, program.VoidLiteral):
        return context.basic_block.constant('')
    elif isinstance(expression, program.AttrLoad):
        return context.attr_lookup(expression.attr)
    elif isinstance(expression, program.Yield):
        value = generate_expression(context, expression.value)
        return context.basic_block.yield_(value)
    elif isinstance(expression, program.Run):
        coroutine = generate_expression(context, expression.coroutine)
        return context.basic_block.run_coroutine(coroutine)
    elif isinstance(expression, program.Resume):
        coroutine = generate_expression(context, expression.coroutine)
        value = generate_expression(context, expression.value)
        return context.basic_block.resume(coroutine, value)
    elif isinstance(expression, program.BinOp):
        lhs = generate_expression(context, expression.lhs)
        rhs = generate_expression(context, expression.rhs)
        operator = operators[expression.operator]
        return context.basic_block.operation(operator, [lhs, rhs])
    elif isinstance(expression, program.FunctionCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        if expression.coroutine_call:
            return context.basic_block.new_coroutine(expression.name, arguments)
        else:
            return context.basic_block.fun_call(expression.name, arguments)
    elif isinstance(expression, program.SysCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.sys_call(expression.name, arguments)
    elif isinstance(expression, program.MethodCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        object_variable = generate_expression(context, expression.obj)
        return expression.obj.type.method(context.basic_block, object_variable, expression.name, arguments)
    elif isinstance(expression, program.ConstructorCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.fun_call('%s.%s' % (expression.ty, expression.name), arguments)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(context, statement):
    if isinstance(statement, program.Assignment):
        var = generate_expression(context, statement.expression)
        context.add(statement.name, var)
    elif isinstance(statement, program.AttrStore):
        var = generate_expression(context, statement.value)
        context.attr_add(statement.attr, var)
    elif isinstance(statement, program.Conditional):
        # FIXME
        assert not statement.true_block.ret
        assert not statement.false_block.ret

        condition_variable = generate_expression(context, statement.expression)
        entry_conditional = context.basic_block.special_conditional(condition_variable, 0, 0)

        true_block = context.function_writer.basic_block()
        entry_conditional.true_block = true_block.index
        true_context = context.new_context(true_block)

        for true_statement in statement.true_block.statements:
            generate_statement(true_context, true_statement)

        last_true_block = true_context.basic_block.index
        true_goto = true_context.basic_block.special_goto(0)

        false_block = context.function_writer.basic_block()
        entry_conditional.false_block = false_block.index
        false_context = context.new_context(false_block)

        for false_statement in statement.false_block.statements:
            generate_statement(false_context, false_statement)

        last_false_block = false_context.basic_block.index
        false_goto = false_block.special_goto(0)

        context.basic_block = context.function_writer.basic_block()
        true_goto.block_index = context.basic_block.index
        false_goto.block_index = context.basic_block.index

        variables = {}
        for variable in set(true_context.variables.keys()) & set(false_context.variables.keys()):
            true_variable = true_context.lookup(variable)
            false_variable = false_context.lookup(variable)
            if true_variable == false_variable:
                variables[variable] = true_variable
            else:
                phi_inputs = [(last_true_block, true_variable), (last_false_block, false_variable)]
                variables[variable] = context.basic_block.phi(phi_inputs)

        context.variables = variables
    elif isinstance(statement, program.While):
        assert not statement.body.ret

        current_index = context.basic_block.index
        entry_goto = context.basic_block.special_goto(0)
        context.basic_block = context.function_writer.basic_block()
        entry_goto.block_index = context.basic_block.index

        variables = {}
        phis = {}
        for name, variable in context.variables.iteritems():
            inputs = [(current_index, variable)]
            variable, phi = context.basic_block.special_phi(inputs)
            phis[name] = phi
            variables[name] = variable
        context.variables = variables

        for body_statement in statement.body.statements:
            generate_statement(context, body_statement)

        last_body_index = context.basic_block.index

        for name, phi in phis.iteritems():
            phi.inputs[last_body_index] = context.lookup(name)

        condition_variable = generate_expression(context, statement.expression)
        body_conditional = context.basic_block.special_conditional(condition_variable, last_body_index, 0)
        context.basic_block = context.function_writer.basic_block()
        body_conditional.false_block = context.basic_block.index
    elif isinstance(statement, program.Expression):
        generate_expression(context, statement)
    else:
        raise NotImplementedError('unknown statement type: %s' % type(statement))

def generate_code_block(context, code_block):
    for statement in code_block.statements:
        generate_statement(context, statement)

    if code_block.ret:
        variable = generate_expression(context, code_block.ret.expression)
        context.basic_block.ret(variable)

def generate_function(program_writer, function):
    parameter_names = function.parameter_names
    parameter_sizes = function.parameter_sizes
    return_size = function.return_type.size
    with program_writer.function(function.name, parameter_sizes, return_size) as (function_writer, variables):
        variables = dict(zip(parameter_names, variables))
        basic_block = function_writer.basic_block()
        context = FunctionContext(function_writer, basic_block, variables)

        generate_code_block(context, function.body)

def generate_coroutine(program_writer, coroutine):
    parameter_names = coroutine.parameter_names
    parameter_sizes = coroutine.parameter_sizes
    return_size = coroutine.yield_type.size
    with program_writer.function(coroutine.name, parameter_sizes, return_size) as (function_writer, variables):
        variables = dict(zip(parameter_names, variables))
        basic_block = function_writer.basic_block()
        context = FunctionContext(function_writer, basic_block, variables)

        generate_code_block(context, coroutine.body)

def generate_record(program_writer, record):
    def generate_constructor(constructor):
        assert not constructor.body.ret

        function_name = '%s.%s' % (record.name, constructor.name)
        parameter_names = constructor.parameter_names
        parameter_sizes = constructor.parameter_sizes
        return_size = record.type.size
        with program_writer.function(function_name, parameter_sizes, return_size) as (function_writer, variables):
            variables = dict(zip(parameter_names, variables))
            basic_block = function_writer.basic_block()
            context = RecordContext(function_writer, basic_block, variables)

            generate_code_block(context, constructor.body)

            arguments = [context.lookup('@%s' % attr) for attr, _ in record.type.attrs]
            result = context.basic_block.operation('pack', arguments)
            context.basic_block.ret(result)

    def generate_method(method):
        function_name = '%s#%s' % (record.name, method.name)
        parameter_names = ['self'] + method.parameter_names
        parameter_sizes = [record.type.size] + method.parameter_sizes
        return_size = method.return_type.size
        with program_writer.function(function_name, parameter_sizes, return_size) as (function_writer, variables):
            basic_block = function_writer.basic_block()

            variable_dict = dict(zip(parameter_names, variables))
            offset = 0
            offset_var = basic_block.constant(struct.pack('>Q', offset))
            for attr, attr_type in record.type.attrs:
                offset += attr_type.size
                new_offset_var = basic_block.constant(struct.pack('>Q', offset))
                var = basic_block.operation('slice', [offset_var, new_offset_var, variables[0]])
                variable_dict['@%s' % attr] = var
                offset_var = new_offset_var

            context = RecordContext(function_writer, basic_block, variable_dict)

            generate_code_block(context, method.body)

    for decl in record.decls:
        if isinstance(decl, program.Constructor):
            generate_constructor(decl)
        elif isinstance(decl, program.Function):
            generate_method(decl)

def generate_service(program_writer, name, instantiations, service_decl):
    def generate_service_method(function_name, function):
        parameter_names = ['self'] + function.parameter_names
        parameter_sizes = [8] + function.parameter_sizes
        return_size = function.return_type.size
        with program_writer.function(function_name, parameter_sizes, return_size) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            variable_dict = dict(zip(parameter_names, variables))
            context = ServiceContext(
                            name,
                            service_decl.dependency_names,
                            service_decl.type.attrs,
                            variables[0],
                            function_writer,
                            basic_block,
                            variable_dict
                        )
            generate_code_block(context, function.body)

    for decl in service_decl.decls:
        if isinstance(decl, program.Private):
            for function in decl.decls:
                function_name = "%s#%s" % (name, function.name)
                generate_service_method(function_name, function)
        elif isinstance(decl, program.Implements):
            interface = decl.interface
            for function in decl.decls:
                function_name = "%s.%s#%s" % (name, interface, function.name)
                generate_service_method(function_name, function)

    for instantiation in instantiations:
        instantiation.dependencies = dict(zip(service_decl.dependency_names, instantiation.service_arguments))

    for dependency_name in service_decl.dependency_names:
        with program_writer.function("%s^%s" % (service_decl.name, dependency_name), [8], 16) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            self_variable = variables[0]
            block = 0
            for instantiation in instantiations:
                service_id = basic_block.constant(struct.pack('>Q', instantiation.service_id))
                v = basic_block.operation('eq', [self_variable, service_id])
                basic_block.conditional(v, block + 1, block + 2)
                basic_block = function_writer.basic_block()
                result = instantiation.dependencies[dependency_name].interface_variable(basic_block)
                basic_block.ret(result)
                basic_block = function_writer.basic_block()
                block += 2
            basic_block.catch_fire_and_die()

    memory_offset = 0
    for attr_name, attr_type in service_decl.type.attrs.iteritems():
        with program_writer.function("%s^%s" % (service_decl.name, attr_name), [8], 8) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            self_variable = variables[0]

            block = 0
            for instantiation in instantiations:
                attr_offset = memory_offset + instantiation.memory_offset
                service_id = basic_block.constant(struct.pack('>Q', instantiation.service_id))
                v = basic_block.operation('eq', [self_variable, service_id])
                basic_block.conditional(v, block + 1, block + 2)
                basic_block = function_writer.basic_block()
                result = basic_block.constant(struct.pack('>Q', attr_offset))
                basic_block.ret(result)
                basic_block = function_writer.basic_block()
                block += 2
            basic_block.catch_fire_and_die()
        memory_offset += attr_type.size

def generate_interface(program_writer, interface, services):
    for name, (parameter_types, return_type) in interface.methods.iteritems():
        function_name = "%s#%s" % (interface.name, name)
        parameter_sizes = [16] + [param.size for param in parameter_types]
        return_size = return_type.size
        with program_writer.function(function_name, parameter_sizes, return_size) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            zero = basic_block.constant(struct.pack('>Q', 0))
            eight = basic_block.constant(struct.pack('>Q', 8))
            sixteen = basic_block.constant(struct.pack('>Q', 16))
            self_type = basic_block.operation('slice', [zero, eight, variables[0]])
            self_id = basic_block.operation('slice', [eight, sixteen, variables[0]])

            block = 0
            for service_name, service_type_id in services:
                service_type = basic_block.constant(struct.pack('>Q', service_type_id))
                v = basic_block.operation('eq', [service_type, self_type])
                basic_block.conditional(v, block + 1, block + 2)
                basic_block = function_writer.basic_block()
                result = basic_block.fun_call("%s.%s#%s" % (service_name, interface.name, name), [self_id] + variables[1:])
                basic_block.ret(result)
                block += 2

            basic_block = function_writer.basic_block()
            basic_block.catch_fire_and_die()

def transitive_closure_services(entry_service):
    services = set()
    stack = [entry_service]
    while stack:
        service = stack.pop()
        if not service in services:
            services.add(service)
            stack.extend(service.service_arguments)
    return services

def group_services(services):
    grouped_services = collections.defaultdict(list)

    for service in services:
        service.service_id = len(grouped_services[service.service])
        grouped_services[service.service].append(service)

    return grouped_services

def generate_code(writer, entry_service, decls):
    with writer as program_writer:
        service_decls = {}
        entry_point = program_types.Interface('EntryPoint', {'main': ([], program_types.bool)})
        interface_types = {'EntryPoint': entry_point}
        for decl in decls:
            if isinstance(decl, program.Function):
                generate_function(program_writer, decl)
            elif isinstance(decl, program.Coroutine):
                generate_coroutine(program_writer, decl)
            elif isinstance(decl, program.Record):
                generate_record(program_writer, decl)
            elif isinstance(decl, program.Service):
                service_decls[decl.name] = decl
            elif isinstance(decl, program.Interface):
                interface_types[decl.name] = decl.type

        service_types = {}
        all_services = transitive_closure_services(entry_service)
        grouped_services = group_services(all_services)
        memory_offset = 0
        for (name, instantiations), service_type_id in zip(grouped_services.iteritems(), itertools.count()):
            service_decl = service_decls[name]
            service_types[name] = service_type_id
            for instantiation in instantiations:
                instantiation.service_type_id = service_type_id
                instantiation.memory_offset = memory_offset
                memory_offset += service_decl.type.attrs_size

        for name, instantiations in grouped_services.iteritems():
            service_decl = service_decls[name]
            generate_service(program_writer, name, instantiations, service_decl)

        services_by_interface = collections.defaultdict(set)
        for name in grouped_services:
            service_decl = service_decls[name]
            for interface in service_decl.type.interfaces:
                services_by_interface[interface].add((name, service_types[name]))

        for interface, services in services_by_interface.iteritems():
            interface_type = interface_types[interface]
            generate_interface(program_writer, interface_type, services)

        with program_writer.function('$main', [], 1) as (function_writer, _):
            with function_writer.basic_block() as block_writer:
                for service in all_services:
                    service_variable = service.service_variable(block_writer)
                    for attr_name, value in service.attrs.iteritems():
                        attr_address = block_writer.fun_call('%s^%s' % (service.service, attr_name), [service_variable])
                        var = block_writer.constant(value)
                        block_writer.store(attr_address, var)

                service = entry_service.interface_variable(block_writer)
                x = block_writer.fun_call("EntryPoint#main", [service])
                block_writer.ret(x)
