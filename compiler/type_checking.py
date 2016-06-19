import program
import program_types
import type_check_code_block

def type_check(decls):
    signatures = {}
    types = {
        'UInt': program_types.uint,
        'Bool': program_types.bool,
        'Void': program_types.void,
        'Byte': program_types.byte
    }
    entry_point = program_types.Interface('EntryPoint', {'main': ([], program_types.bool)})
    interface_types = {'EntryPoint': entry_point}

    def type_check_function(function):
        context = type_check_code_block.TypeCheckingContext(
                        signatures,
                        types,
                        {},
                        None,
                        None,
                        function.return_type,
                        {},
                        False,
                        dict(function.parameters)
                    )

        type_check_code_block.type_check_code_block(context, function.body)

    def type_check_coroutine(coroutine):
        context = type_check_code_block.TypeCheckingContext(
                        signatures,
                        types,
                        {},
                        coroutine.receive_type,
                        coroutine.yield_type,
                        program_types.void,
                        {},
                        False,
                        dict(coroutine.parameters)
                    )

        type_check_code_block.type_check_code_block(context, coroutine.body)

    def type_check_constructor(attr_types, constructor):
        context = type_check_code_block.TypeCheckingContext(
                        signatures,
                        types,
                        {},
                        None,
                        None,
                        program_types.void,
                        attr_types,
                        True,
                        dict(constructor.parameters)
                    )

        type_check_code_block.type_check_code_block(context, constructor.body)

    def type_check_method(self_type, attr_types, method, store_attributes=False):
        scope = dict(method.parameters)
        scope['self'] = self_type
        context = type_check_code_block.TypeCheckingContext(
                        signatures,
                        types,
                        {},
                        None,
                        None,
                        method.return_type,
                        attr_types,
                        store_attributes,
                        scope
                    )

        type_check_code_block.type_check_code_block(context, method.body)

    function_decls = []
    coroutine_decls = []
    record_decls = []
    interface_decls = []
    service_decls = []
    entry = None
    for decl in decls:
        if isinstance(decl, program.Function):
            function_decls.append(decl)
        elif isinstance(decl, program.Coroutine):
            coroutine_decls.append(decl)
        elif isinstance(decl, program.Record):
            record_decls.append(decl)
        elif isinstance(decl, program.Interface):
            interface_decls.append(decl)
        elif isinstance(decl, program.Service):
            service_decls.append(decl)
        elif isinstance(decl, program.Entry):
            assert not entry
            entry = decl

    for record in record_decls:
        attrs = []

        for decl in record.decls:
            if isinstance(decl, program.Attr):
                decl.type = decl.type.resolve_type(types)
                attrs.append((decl.name, decl.type))

        record.type = program_types.Record(record.name, attrs, {}, {})
        assert not record.name in types
        types[record.name] = record.type

    for record in record_decls:
        constructor_signatures = record.type.constructor_signatures
        methods = record.type.methods

        for decl in record.decls:
            if isinstance(decl, program.Constructor):
                decl.resolve_types(types)
                constructor_signatures[decl.name] = decl.parameter_types
            elif isinstance(decl, program.Function):
                decl.resolve_types(types)
                methods[decl.name] = decl.signature

    for record in record_decls:
        for decl in record.decls:
            if isinstance(decl, program.Constructor):
                type_check_constructor(dict(record.type.attrs), decl)
            elif isinstance(decl, program.Function):
                type_check_method(record.type, dict(record.type.attrs), decl)

    for interface in interface_decls:
        methods = {}

        for decl in interface.decls:
            decl.resolve_types(types)
            methods[decl.name] = (decl.parameters, decl.return_type)

        interface.type = program_types.Interface(interface.name, methods)
        assert not interface.name in interface_types
        interface_types[interface.name] = interface.type

    services = {}
    for service in service_decls:
        attrs = {}
        dependency_names = {name for name, interface_name in service.dependencies}
        dependencies = [(name, interface_types[interface_name]) for name, interface_name in service.dependencies]
        constructor_signatures = {}
        interfaces = set()
        private_methods = {}

        for service_decl in service.decls:
            if isinstance(service_decl, program.Attr):
                service_decl.type = service_decl.type.resolve_type(types)
                assert not service_decl.name in attrs
                assert not service_decl.name in dependency_names
                attrs[service_decl.name] = service_decl.type
            elif isinstance(service_decl, program.Implements):
                interface = interface_types[service_decl.interface]
                methods = {}

                for method_decl in service_decl.decls:
                    method_decl.resolve_types(types)
                    methods[method_decl.name] = method_decl.signature

                assert methods == interface.methods
                interfaces.add(service_decl.interface)
            elif isinstance(service_decl, program.Private):
                for private_decl in service_decl.decls:
                    private_decl.resolve_types(types)
                    private_methods[private_decl.name] = private_decl.signature
            elif isinstance(service_decl, program.Constructor):
                service_decl.resolve_types(types)
                constructor_signatures[service_decl.name] = service_decl.parameter_types
        service.type = program_types.Service(service.name, dependencies, attrs, constructor_signatures, interfaces)
        services[service.name] = service.type
        service.private_type = program_types.PrivateService(service.name, private_methods)

    for function in function_decls:
        assert not function.name in signatures
        function.resolve_types(types)
        signatures[function.name] = type_check_code_block.FunctionSignature(
                                            function.parameter_types,
                                            function.return_type
                                        )

    for coroutine in coroutine_decls:
        assert not coroutine.name in signatures
        coroutine.resolve_types(types)
        arg_types = coroutine.parameter_types
        signatures[coroutine.name] = type_check_code_block.CoroutineSignature(
                                            coroutine.parameter_types,
                                            coroutine.receive_type,
                                            coroutine.yield_type
                                        )

    for service in service_decls:
        all_attrs = service.type.all_attrs
        for service_decl in service.decls:
            if isinstance(service_decl, program.Implements):
                for method_decl in service_decl.decls:
                    type_check_method(service.private_type, all_attrs, method_decl, True)
            elif isinstance(service_decl, program.Private):
                for private_decl in service_decl.decls:
                    type_check_method(service.private_type, all_attrs, private_decl, True)
            elif isinstance(service_decl, program.Constructor):
                type_check_constructor(attrs, service_decl)

    for function in function_decls:
        type_check_function(function)

    for coroutine in coroutine_decls:
        type_check_coroutine(coroutine)

    if entry:
        context = type_check_code_block.TypeCheckingContext(signatures, types, services, None, None, entry_point, {}, False, {})
        type_check_code_block.type_check_code_block(context, entry.body)
