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

    def has(self, name):
        return name in self.variables

    def lookup(self, name):
        return self.variables[name]

    def delete(self, name):
        del self.variables[name]

    def new_context(self, basic_block):
        raise NotImplementedError()

    def attr_add(self, name, value):
        raise NotImplementedError()

    def attr_lookup(self, name):
        raise NotImplementedError()

class FunctionContext(GenerationContext):
    def new_context(self, basic_block):
        return FunctionContext(self.current_module_name, self.function_writer, basic_block, dict(self.variables))

class ServiceContext(GenerationContext):
    def __init__(self, current_module_name, name, dependencies, attrs, self_variable, function_writer, basic_block, variables):
        self.current_module_name = current_module_name
        self.name = name
        self.dependencies = dependencies
        self.attrs = attrs
        self.function_writer = function_writer
        self.basic_block = basic_block
        self.variables = variables
        self.variables['self'] = self_variable

    def new_context(self, basic_block):
        return ServiceContext(
                    self.current_module_name,
                    self.name,
                    self.dependencies,
                    self.attrs,
                    self.variables['self'],
                    self.function_writer,
                    basic_block,
                    dict(self.variables)
                )

    def attr_lookup(self, name):
        self.variables['self'], self_variable = self.basic_block.dup(self.variables['self'])
        if name in self.dependencies:
            return self.basic_block.fun_call('%s^%s' % (self.name, name), [self_variable])
        elif name in self.attrs:
            offset = self.basic_block.fun_call('%s^%s' % (self.name, name), [self_variable])
            return self.basic_block.load(offset)
        else:
            raise NotImplementedError()

    def attr_add(self, name, value):
        self.variables['self'], self_variable = self.basic_block.dup(self.variables['self'])
        offset = self.basic_block.fun_call('%s^%s' % (self.name, name), [self_variable])
        self.basic_block.store(offset, value)

def do_while(context, fn):
    current_index = context.basic_block.index
    entry_goto = context.basic_block.special_goto(0)
    context.basic_block = context.function_writer.basic_block()
    first_body_block = context.basic_block.index
    entry_goto.block_index = first_body_block

    variables = {}
    phis = {}
    for name, variable in context.variables.iteritems():
        inputs = [(current_index, variable)]
        variable, phi = context.basic_block.special_phi(inputs)
        phis[name] = phi
        variables[name] = variable
    context.variables = variables

    condition_variable = fn(context)

    if context.basic_block:
        last_body_index = context.basic_block.index

        for name, phi in phis.iteritems():
            phi.inputs[last_body_index] = context.lookup(name)

        body_conditional = context.basic_block.special_conditional(condition_variable, first_body_block, 0)
        context.basic_block = context.function_writer.basic_block()
        body_conditional.false_block = context.basic_block.index

def do_while_block(context, body, expression):
    if body.terminator:
        for body_statement in body.statements:
            generate_statement(context, body_statement)
    else:
        def gen_body(context):
            for body_statement in body.statements:
                generate_statement(context, body_statement)
            if context.basic_block is not None:
                return generate_expression(context, expression)

        do_while(context, gen_body)

def if_then_else(context, condition_variable, true_code_block, false_code_block):
    entry_conditional = context.basic_block.special_conditional(condition_variable, 0, 0)

    true_block = context.function_writer.basic_block()
    entry_conditional.true_block = true_block.index
    true_context = context.new_context(true_block)

    true_code_block(true_context)
    true_terminated = (true_context.basic_block is None) or true_context.basic_block.terminated

    if not true_terminated:
        last_true_block = true_context.basic_block.index
        true_goto = true_context.basic_block.special_goto(0)

    false_block = context.function_writer.basic_block()
    entry_conditional.false_block = false_block.index
    false_context = context.new_context(false_block)

    false_code_block(false_context)
    false_terminated = (false_context.basic_block is None) or false_context.basic_block.terminated

    if not false_terminated:
        last_false_block = false_context.basic_block.index
        false_goto = false_context.basic_block.special_goto(0)

    if not true_terminated or not false_terminated:
        context.basic_block = context.function_writer.basic_block()
    else:
        context.basic_block = None

    if not true_terminated:
        true_goto.block_index = context.basic_block.index

    if not false_terminated:
        false_goto.block_index = context.basic_block.index

    if not true_terminated and not false_terminated:
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
    elif not true_terminated:
        context.variables = true_context.variables
    elif not false_terminated:
        context.variables = false_context.variables
    else:
        context.variables = {}

def if_then_else_block(context, condition_variable, true_code_block, false_code_block):
    def true_block(context):
        for true_statement in true_code_block.statements:
            generate_statement(context, true_statement)
        generate_terminator(context, true_code_block.terminator)

    def false_block(context):
        for false_statement in false_code_block.statements:
            generate_statement(context, false_statement)
        generate_terminator(context, false_code_block.terminator)

    if_then_else(context, condition_variable, true_block, false_block)

list_operators = {
    '+': 'list.extend'
}

uint_operators = {
    '<': 'uint.lt',
    '>': 'uint.gt',
    '<=': 'uint.le',
    '>=': 'uint.ge',
    '+': 'uint.add',
    '-': 'uint.sub',
    '*': 'uint.mul',
    '/': 'uint.div',
    '==': 'uint.eq',
    '!=': 'uint.ne'
}

bytestring_operators = {
    '==': 'bytestring.eq'
}

string_operators = {
    '==': 'string.eq',
    '+': 'string.concat'
}

bool_operators = {
    'and': 'and',
    'or': 'or'
}

byte_operators = {
    '==': 'byte.eq'
}

char_operators = {
    '==': 'char.eq'
}

def operator_name(operator, lhs_type):
    if isinstance(lhs_type, program_types.Instantiation) and lhs_type.constructor == program_types.list:
        return list_operators[operator]
    elif lhs_type == program_types.uint:
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
        var, var_copy = context.basic_block.dup(context.lookup(expression.name))
        context.add(expression.name, var)
        return var_copy
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
    elif isinstance(expression, program.Not):
        value = generate_expression(context, expression.expression)
        return context.basic_block.operation('not', [value])
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
        else:
            raise NotImplementedError('unknown call type: %s' % type(expression.call))
    elif isinstance(expression, program.SysCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.sys_call(expression.name, arguments)
    elif isinstance(expression, program.OpCall):
        arguments = [generate_expression(context, argument) for argument in expression.arguments]
        return context.basic_block.operation(expression.name, arguments)
    elif isinstance(expression, program.TupleConstructor):
        values = [generate_expression(context, value) for value in expression.values]
        return context.basic_block.operation('list.pack', values)
    elif isinstance(expression, program.ListConstructor):
        values = [generate_expression(context, value) for value in expression.values]
        return context.basic_block.operation('list.pack', values)
    elif isinstance(expression, program.Annotated):
        return generate_expression(context, expression.expression)
    else:
        raise NotImplementedError('unknown expression type: %s' % type(expression))

def generate_statement(context, statement):
    assert context.basic_block is not None
    if isinstance(statement, program.Assignment):
        assert statement.name != 'self'
        var = generate_expression(context, statement.expression)
        context.add(statement.name, var)
    elif isinstance(statement, program.AttrStore):
        var = generate_expression(context, statement.value)
        context.attr_add(statement.attr, var)
    elif isinstance(statement, program.TupleDestructure):
        var = generate_expression(context, statement.expression)
        for name, i in zip(statement.names, itertools.count()):
            i_var = context.basic_block.constant_uint(i)
            var, var1 = context.basic_block.dup(var)
            v = context.basic_block.operation('list.index', [var1, i_var])
            context.add(name, v)
    elif isinstance(statement, program.Conditional):
        condition_variable = generate_expression(context, statement.expression)
        if_then_else_block(context, condition_variable, statement.true_block, statement.false_block)
    elif isinstance(statement, program.For):
        assert not statement.body.terminator

        coroutine = generate_expression(context, statement.expression)
        coroutine1 = context.basic_block.copy()
        coroutine2 = context.basic_block.copy()

        last_value = context.basic_block.run_coroutine(coroutine1)
        done = context.basic_block.operation('is_done', [coroutine2])

        coroutine_var_name = '$coroutine_%s' % id(statement)

        context.add(coroutine_var_name, coroutine)
        context.add(statement.name, last_value)

        def true_block(context):
            pass

        def false_block(context):
            def fn(context):
                for st in statement.body.statements:
                    generate_statement(context, st)

                coroutine = context.lookup(coroutine_var_name)
                coroutine = context.basic_block.move(coroutine)
                coroutine1 = context.basic_block.copy()
                coroutine2 = context.basic_block.copy()
                context.add(coroutine_var_name, coroutine)

                v = context.basic_block.void()
                last_value = context.basic_block.resume(coroutine1, v)
                context.add(statement.name, last_value)

                done = context.basic_block.operation('is_done', [coroutine2])
                return context.basic_block.operation('not', [done])

            do_while(context, fn)

        if_then_else(context, done, true_block, false_block)
        context.delete(statement.name)
        context.delete(coroutine_var_name)
    elif isinstance(statement, program.While):
        do_while_block(context, statement.body, statement.expression)
    elif isinstance(statement, program.Match):
        var = generate_expression(context, statement.expression)
        var, var1 = context.basic_block.dup(var)
        zero = context.basic_block.constant_uint(0)
        name = context.basic_block.operation('list.index', [var1, zero])

        contexts = []
        gotos = []

        for clause in statement.clauses:
            clause_name = context.basic_block.constant_bytestring(clause.name)
            name, name1 = context.basic_block.dup(name)
            v = context.basic_block.operation('bytestring.eq', [name1, clause_name])
            cond = context.basic_block.special_conditional(v, 0, 0)

            clause_block = context.function_writer.basic_block()
            cond.true_block = clause_block.index
            clause_context = context.new_context(clause_block)

            index = 1
            var1 = var
            for param in clause.parameters:
                var1, var2 = clause_context.basic_block.dup(var1)
                index_var = clause_context.basic_block.constant_uint(index)
                param_var = clause_context.basic_block.operation('list.index', [var2, index_var])
                clause_context.add(param, param_var)
                index += 1

            for clause_statement in clause.block.statements:
                generate_statement(clause_context, clause_statement)

            if clause_context.basic_block is not None:
                if clause.block.terminator:
                    generate_terminator(clause_context, clause.block.terminator)
                else:
                    gotos.append(clause_context.basic_block.special_goto(0))
                    contexts.append(clause_context)

            context.basic_block = context.function_writer.basic_block()
            cond.false_block = context.basic_block.index

        context.basic_block.catch_fire_and_die()

        if contexts:
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
        else:
            context.basic_block = None
            context.variables = {}
    elif isinstance(statement, program.Debug):
        value = generate_expression(context, statement.expression)
        context.basic_block.debug(value)
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

    if context.basic_block is not None:
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
        if context.basic_block is not None and not function.body.terminator:
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

def generate_enum(program_writer, enum):
    for constructor in enum.constructors:
        name = "%s::%s" % (enum.module_interface.name, constructor.name)
        with program_writer.function(name, len(constructor.types)) as (function_writer, variables):
            with function_writer.basic_block() as basic_block:
                name = basic_block.constant_bytestring(constructor.name)
                result = basic_block.operation('list.pack', [name] + variables)
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
            assert isinstance(decl.interface_type, program_types.Instantiation)
            interface = decl.interface_type.constructor
            for function in decl.decls:
                function_name = "%s.%s#%s" % (name, interface.name, function.name)
                generate_service_method(function_name, function)

def generate_service_instantiations(program_writer, instantiations, service_decl):
    name = service_decl.name
    for instantiation in instantiations:
        instantiation.dependencies = dict(zip(service_decl.dependency_names, instantiation.service_arguments))

    for dependency_name in service_decl.dependency_names:
        with program_writer.function("%s^%s" % (service_decl.name, dependency_name), 1) as (function_writer, variables):
            basic_block = function_writer.basic_block()
            self_variable = variables[0]
            block = 0
            for instantiation in instantiations:
                service_id = basic_block.constant_uint(instantiation.service_id)
                self_variable, self_variable1 = basic_block.dup(self_variable)
                v = basic_block.operation('uint.eq', [self_variable1, service_id])
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
                self_variable, self_variable1 = basic_block.dup(self_variable)
                v = basic_block.operation('uint.eq', [self_variable1, service_id])
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

            self_var, self_var1 = basic_block.dup(variables[0])
            zero = basic_block.constant_uint(0)
            one = basic_block.constant_uint(1)

            self_type = basic_block.operation('list.index', [self_var, zero])
            self_id = basic_block.operation('list.index', [self_var1, one])

            block = 0
            for service_name, service_type_id in services:
                self_type, self_type1 = basic_block.dup(self_type)

                service_type = basic_block.constant_uint(service_type_id)
                v = basic_block.operation('uint.eq', [service_type, self_type1])
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
        generate_service_instantiations(program_writer, instantiations, service_decl)

    services_by_interface = collections.defaultdict(set)
    for name in grouped_services:
        service_decl = service_decls[name]
        for interface in service_decl.type.interfaces:
            services_by_interface[interface.constructor].add((name, service_types[name]))

    for interface_type, services in services_by_interface.iteritems():
        generate_interface(program_writer, interface_type, services)

    with program_writer.function('$main', 0) as (function_writer, _):
        with function_writer.basic_block() as block_writer:
            for service in all_services:
                service_variable = service.service_variable(block_writer)
                for attr_name, value in service.attrs.iteritems():
                    service_variable, service_variable1 = block_writer.dup(service_variable)
                    attr_address = block_writer.fun_call('%s^%s' % (service.service, attr_name), [service_variable1])
                    var = value.write_out(block_writer)
                    block_writer.store(attr_address, var)

            service = entry_service.interface_variable(block_writer)
            x = block_writer.fun_call("EntryPoint#main", [service])
            block_writer.ret(x)
