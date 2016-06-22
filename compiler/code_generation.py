import collections
import itertools
import program
import program_types
import type_check_code_block

class GenerationContext(object):
    def __init__(self, current_module_name, function_writer, basic_block, variables):
        self.current_module_name = current_module_name
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
        return FunctionContext(self.current_module_name, self.function_writer, basic_block, dict(self.variables))

class RecordContext(GenerationContext):
    def new_context(self, basic_block):
        return RecordContext(self.current_module_name, self.function_writer, basic_block, dict(self.variables))

    def attr_add(self, name, value):
        self.add('@%s' % name, value)

    def attr_lookup(self, name):
        return self.lookup('@%s' % name)

class ServiceContext(GenerationContext):
    def __init__(self, current_module_name, name, dependencies, attrs, self_variable, function_writer, basic_block, variables):
        self.current_module_name = current_module_name
        self.name = name
        self.dependencies = dependencies
        self.attrs = attrs
        self.self_variable = self_variable
        self.function_writer = function_writer
        self.basic_block = basic_block
        self.variables = variables

    def new_context(self, basic_block):
        return ServiceContext(
                    self.current_module_name,
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
            offset = self.basic_block.fun_call('%s^%s' % (self.name, name), [self.self_variable])
            return self.basic_block.load(offset)
        else:
            raise NotImplementedError()

    def attr_add(self, name, value):
        offset = self.basic_block.fun_call('%s^%s' % (self.name, name), [self.self_variable])
        self.basic_block.store(offset, value)

uint_operators = {
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

bytestring_operators = {
    '==': 'bytestring_eq'
}

string_operators = {
    '==': 'string_eq'
}

bool_operators = {}

byte_operators = {
    '==': 'byte_eq'
}

char_operators = {
    '==': 'char_eq'
}

def operator_name(operator, lhs_type):
    if lhs_type == program_types.uint:
        return uint_operators[operator]
    elif lhs_type == program_types.bytestring:
        return bytestring_operators[operator]
    elif lhs_type == program_types.string:
        return string_operators[operator]
    elif lhs_type == program_types.bool:
        return bool_operators[operator]
    elif lhs_type == program_types.byte:
        return byte_operators[operator]
    elif lhs_type == program_types.char:
        return char_operators[operator]
    else:
        raise NotImplementedError()

def generate_expression(context, expression):
    if isinstance(expression, program.Variable):
        return context.lookup(expression.name)
    elif isinstance(expression, program.CharLiteral):
        return context.basic_block.constant_char(expression.b)
    elif isinstance(expression, program.NumberLiteral):
        return context.basic_block.constant_uint(expression.n)
    elif isinstance(expression, program.BoolLiteral):
        return context.basic_block.constant_bool(expression.b)
    elif isinstance(expression, program.VoidLiteral):
        return context.basic_block.void()
    elif isinstance(expression, program.StringLiteral):
        return context.basic_block.constant_string(expression.v)
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
    elif isinstance(expression, program.IsDone):
        coroutine = generate_expression(context, expression.coroutine)
        return context.basic_block.operation('is_done', [coroutine])
    elif isinstance(expression, program.BinOp):
        lhs = generate_expression(context, expression.lhs)
        rhs = generate_expression(context, expression.rhs)
        operator = operator_name(expression.operator, expression.lhs.type)
        return context.basic_block.operation(operator, [lhs, rhs])
    elif isinstance(expression, program.Call):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        function = expression.function_name
        if isinstance(expression.call, type_check_code_block.FunctionCall):
            name = "%s::%s" % (expression.call.module.name, function)
            if expression.call.coroutine_call:
                return context.basic_block.new_coroutine(name, arguments)
            else:
                return context.basic_block.fun_call(name, arguments)
        elif isinstance(expression.call, type_check_code_block.MethodCall):
            obj = expression.call.obj
            object_variable = generate_expression(context, obj)
            return obj.type.method(context.basic_block, object_variable, function, arguments)
        elif isinstance(expression.call, type_check_code_block.RecordConstructorCall):
            return context.basic_block.fun_call('%s.%s' % (expression.call.record, function), arguments)
        else:
            raise NotImplementedError('unknown call type: %s' % type(expression.call))
    elif isinstance(expression, program.SysCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.sys_call(expression.name, arguments)
    elif isinstance(expression, program.TupleConstructor):
        values = [generate_expression(context, value) for value in expression.values]
        return context.basic_block.operation('pack', values)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(context, statement):
    if isinstance(statement, program.Assignment):
        var = generate_expression(context, statement.expression)
        context.add(statement.name, var)
    elif isinstance(statement, program.AttrStore):
        var = generate_expression(context, statement.value)
        context.attr_add(statement.attr, var)
    elif isinstance(statement, program.TupleDestructure):
        var = generate_expression(context, statement.expression)
        for name, i in zip(statement.names, itertools.count()):
            i_var = context.basic_block.constant_uint(i)
            v = context.basic_block.operation('index', [var, i_var])
            context.add(name, v)
    elif isinstance(statement, program.Conditional):
        condition_variable = generate_expression(context, statement.expression)
        entry_conditional = context.basic_block.special_conditional(condition_variable, 0, 0)

        true_block = context.function_writer.basic_block()
        entry_conditional.true_block = true_block.index
        true_context = context.new_context(true_block)

        for true_statement in statement.true_block.statements:
            generate_statement(true_context, true_statement)
        generate_terminator(true_context, statement.true_block.terminator)

        if not statement.true_block.terminator:
            last_true_block = true_context.basic_block.index
            true_goto = true_context.basic_block.special_goto(0)

        false_block = context.function_writer.basic_block()
        entry_conditional.false_block = false_block.index
        false_context = context.new_context(false_block)

        for false_statement in statement.false_block.statements:
            generate_statement(false_context, false_statement)
        generate_terminator(false_context, statement.false_block.terminator)

        if not statement.false_block.terminator:
            last_false_block = false_context.basic_block.index
            false_goto = false_context.basic_block.special_goto(0)

        context.basic_block = context.function_writer.basic_block()

        if not statement.true_block.terminator:
            true_goto.block_index = context.basic_block.index

        if not statement.false_block.terminator:
            false_goto.block_index = context.basic_block.index

        if not statement.true_block.terminator and not statement.false_block.terminator:
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
        elif not statement.true_block.terminator:
            context.variables = true_context.variables
        elif not statement.false_block.terminator:
            context.variables = false_context.variables
        else:
            context.variables = {}
    elif isinstance(statement, program.While):
        assert not statement.body.terminator

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
    elif isinstance(statement, program.Match):
        var = generate_expression(context, statement.expression)
        zero = context.basic_block.constant_uint(0)
        name = context.basic_block.operation('index', [var, zero])

        contexts = []
        gotos = []

        for clause in statement.clauses:
            clause_name = context.basic_block.constant_bytestring(clause.name)
            v = context.basic_block.operation('bytestring_eq', [name, clause_name])
            cond = context.basic_block.special_conditional(v, 0, 0)

            clause_block = context.function_writer.basic_block()
            cond.true_block = clause_block.index
            clause_context = context.new_context(clause_block)

            index = 1
            for param in clause.parameters:
                index_var = clause_context.basic_block.constant_uint(index)
                param_var = clause_context.basic_block.operation('index', [var, index_var])
                clause_context.add(param, param_var)
                index += 1

            for clause_statement in clause.block.statements:
                generate_statement(clause_context, clause_statement)

            gotos.append(clause_context.basic_block.special_goto(0))
            contexts.append(clause_context)

            context.basic_block = context.function_writer.basic_block()
            cond.false_block = context.basic_block.index

        context.basic_block.catch_fire_and_die()
        context.basic_block = context.function_writer.basic_block()
        for goto in gotos:
            goto.block_index = context.basic_block.index

        variable_names = reduce(lambda a, b: a & b, [set(ctx.variables.keys()) for ctx in contexts])
        variables = {}
        for variable_name in variable_names:
            vars = [ctx.lookup(variable_name) for ctx in contexts]
            if all([v == vars[0] for v in vars]):
                variables[variable_name] = vars[0]
            else:
                phi_inputs = [(ctx.basic_block.index, ctx.lookup(variable_name)) for ctx in contexts]
                variables[variable_name] = context.basic_block.phi(phi_inputs)

        context.variables = variables
    elif isinstance(statement, program.Expression):
        generate_expression(context, statement)
    else:
        raise NotImplementedError('unknown statement type: %s' % type(statement))

def generate_terminator(context, terminator):
    if terminator:
        if isinstance(terminator, program.Return):
            variable = generate_expression(context, terminator.expression)
            context.basic_block.ret(variable)
        elif isinstance(terminator, program.Throw):
            exception = generate_expression(context, terminator.exception)
            context.basic_block.throw(exception)
        else:
            raise NotImplementedError('unknown terminator type: %s' % type(terminator))

def generate_code_block(context, code_block):
    for statement in code_block.statements:
        generate_statement(context, statement)

    generate_terminator(context, code_block.terminator)

def generate_function(program_writer, function):
    parameter_names = function.parameter_names
    num_parameters = function.num_parameters
    name = "%s::%s" % (function.module_interface.name, function.name)
    with program_writer.function(name, num_parameters) as (function_writer, variables):
        variables = dict(zip(parameter_names, variables))
        basic_block = function_writer.basic_block()
        context = FunctionContext(function.module_interface.name, function_writer, basic_block, variables)

        generate_code_block(context, function.body)
        if not function.body.terminator:
            context.basic_block.catch_fire_and_die()

def generate_coroutine(program_writer, coroutine):
    parameter_names = coroutine.parameter_names
    num_parameters = coroutine.num_parameters
    name = "%s::%s" % (coroutine.module_interface.name, coroutine.name)
    with program_writer.function(name, num_parameters) as (function_writer, variables):
        variables = dict(zip(parameter_names, variables))
        basic_block = function_writer.basic_block()
        context = FunctionContext(coroutine.module_interface.name, function_writer, basic_block, variables)

        generate_code_block(context, coroutine.body)

def generate_record(program_writer, record):
    def generate_constructor(constructor):
        assert not constructor.body.terminator

        function_name = '%s.%s' % (record.name, constructor.name)
        parameter_names = constructor.parameter_names
        num_parameters = constructor.num_parameters
        with program_writer.function(function_name, num_parameters) as (function_writer, variables):
            variables = dict(zip(parameter_names, variables))
            basic_block = function_writer.basic_block()
            context = RecordContext(record.module_interface.name, function_writer, basic_block, variables)

            generate_code_block(context, constructor.body)

            arguments = [context.lookup('@%s' % attr) for attr, _ in record.type.attrs]
            result = context.basic_block.operation('pack', arguments)
            context.basic_block.ret(result)

    def generate_method(method):
        function_name = '%s#%s' % (record.name, method.name)
        parameter_names = ['self'] + method.parameter_names
        num_parameters = 1 + method.num_parameters
        with program_writer.function(function_name, num_parameters) as (function_writer, variables):
            basic_block = function_writer.basic_block()

            variable_dict = dict(zip(parameter_names, variables))
            offset = 0
            offset_var = basic_block.constant_uint(offset)
            for attr, attr_type in record.type.attrs:
                offset += 1
                new_offset_var = basic_block.constant_uint(offset)
                var = basic_block.operation('index', [variables[0], offset_var])
                variable_dict['@%s' % attr] = var
                offset_var = new_offset_var

            context = RecordContext(record.module_interface.name, function_writer, basic_block, variable_dict)

            generate_code_block(context, method.body)

    for decl in record.decls:
        if isinstance(decl, program.Constructor):
            generate_constructor(decl)
        elif isinstance(decl, program.Function):
            generate_method(decl)

def generate_enum(program_writer, enum):
    for constructor in enum.constructors:
        name = "%s::%s" % (enum.module_interface.name, constructor.name)
        with program_writer.function(name, len(constructor.types)) as (function_writer, variables):
            with function_writer.basic_block() as basic_block:
                name = basic_block.constant_bytestring(constructor.name)
                result = basic_block.operation('pack', [name] + variables)
                basic_block.ret(result)

def generate_service_methods(program_writer, service_decl):
    name = service_decl.name

    def generate_service_method(function_name, function):
        parameter_names = ['self'] + function.parameter_names
        num_parameters = 1 + function.num_parameters
        with program_writer.function(function_name, num_parameters) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            variable_dict = dict(zip(parameter_names, variables))
            context = ServiceContext(
                            service_decl.module_interface.name,
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
                function_name = "%s.%s#%s" % (name, interface.name, function.name)
                generate_service_method(function_name, function)

def generate_service_instantiations(program_writer, name, instantiations, service_decl):
    for instantiation in instantiations:
        instantiation.dependencies = dict(zip(service_decl.dependency_names, instantiation.service_arguments))

    for dependency_name in service_decl.dependency_names:
        with program_writer.function("%s^%s" % (service_decl.name, dependency_name), 1) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            self_variable = variables[0]
            block = 0
            for instantiation in instantiations:
                service_id = basic_block.constant_uint(instantiation.service_id)
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
        with program_writer.function("%s^%s" % (service_decl.name, attr_name), 1) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            self_variable = variables[0]

            block = 0
            for instantiation in instantiations:
                attr_offset = memory_offset + instantiation.memory_offset
                service_id = basic_block.constant_uint(instantiation.service_id)
                v = basic_block.operation('eq', [self_variable, service_id])
                basic_block.conditional(v, block + 1, block + 2)
                basic_block = function_writer.basic_block()
                result = basic_block.constant_uint(attr_offset)
                basic_block.ret(result)
                basic_block = function_writer.basic_block()
                block += 2
            basic_block.catch_fire_and_die()
        memory_offset += 1

def generate_interface(program_writer, interface, services):
    for name, (parameter_types, return_type) in interface.methods.iteritems():
        function_name = "%s#%s" % (interface.name, name)
        num_parameters = 1 + len(parameter_types)
        with program_writer.function(function_name, num_parameters) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            zero = basic_block.constant_uint(0)
            one = basic_block.constant_uint(1)
            self_type = basic_block.operation('index', [variables[0], zero])
            self_id = basic_block.operation('index', [variables[0], one])

            block = 0
            for service_name, service_type_id in services:
                service_type = basic_block.constant_uint(service_type_id)
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

def generate_module(program_writer, module):
    for decl in module.decls:
        if isinstance(decl, program.Function):
            generate_function(program_writer, decl)
        elif isinstance(decl, program.Coroutine):
            generate_coroutine(program_writer, decl)
        elif isinstance(decl, program.Record):
            generate_record(program_writer, decl)
        elif isinstance(decl, program.Enum):
            generate_enum(program_writer, decl)
        elif isinstance(decl, program.Service):
            generate_service_methods(program_writer, decl)

def group_services(services):
    grouped_services = collections.defaultdict(list)

    for service in services:
        service.service_id = len(grouped_services[service.service])
        grouped_services[service.service].append(service)

    return grouped_services

def generate_entry(program_writer, entry_service, modules):
    service_decls = {}
    for module_name, module in modules.iteritems():
        for decl in module.decls:
            if isinstance(decl, program.Service):
                service_decls[decl.name] = decl

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
            memory_offset += len(service_decl.type.attrs)

    for name, instantiations in grouped_services.iteritems():
        service_decl = service_decls[name]
        generate_service_instantiations(program_writer, name, instantiations, service_decl)

    services_by_interface = collections.defaultdict(set)
    for name in grouped_services:
        service_decl = service_decls[name]
        for interface in service_decl.type.interfaces:
            services_by_interface[interface].add((name, service_types[name]))

    for interface_type, services in services_by_interface.iteritems():
        generate_interface(program_writer, interface_type, services)

    with program_writer.function('$main', 0) as (function_writer, _):
        with function_writer.basic_block() as block_writer:
            for service in all_services:
                service_variable = service.service_variable(block_writer)
                for attr_name, value in service.attrs.iteritems():
                    attr_address = block_writer.fun_call('%s^%s' % (service.service, attr_name), [service_variable])
                    var = value.write_out(block_writer)
                    block_writer.store(attr_address, var)

            service = entry_service.interface_variable(block_writer)
            x = block_writer.fun_call("EntryPoint#main", [service])
            block_writer.ret(x)
