import program
import program_types
import type_check_code_block
import module_interface

def type_check(modules):
    module_interfaces = {}
    for module_name, module in modules.iteritems():
        module.interface = module_interface.ModuleInterface(module_name, module.imports)
        module_interfaces[module_name] = module.interface

    types = {
        'UInt': program_types.uint,
        'Bool': program_types.bool,
        'Void': program_types.void,
        'Byte': program_types.byte,
        'ByteString': program_types.bytestring,
        'Char': program_types.char,
        'String': program_types.string
    }
    entry_point = program_types.Interface('EntryPoint', {'main': ([], program_types.bool)})
    interface_types = {'EntryPoint': entry_point}

    def type_check_function(function):
        context = type_check_code_block.TypeCheckingContext(
                        module_interfaces,
                        function.module_interface,
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
                        module_interfaces,
                        coroutine.module_interface,
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

    def type_check_constructor(current_module, attr_types, constructor):
        context = type_check_code_block.TypeCheckingContext(
                        module_interfaces,
                        current_module,
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

    def type_check_method(current_module, self_type, attr_types, method, store_attributes=False):
        scope = dict(method.parameters)
        scope['self'] = self_type
        context = type_check_code_block.TypeCheckingContext(
                        module_interfaces,
                        current_module,
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
    enum_decls = []
    interface_decls = []
    service_decls = []
    entry_blocks = []
    for module_name, module in modules.iteritems():
        entry = None
        for decl in module.decls:
            decl.module_interface = module.interface
            if isinstance(decl, program.Function):
                function_decls.append(decl)
            elif isinstance(decl, program.Coroutine):
                coroutine_decls.append(decl)
            elif isinstance(decl, program.Record):
                record_decls.append(decl)
            elif isinstance(decl, program.Enum):
                enum_decls.append(decl)
            elif isinstance(decl, program.Interface):
                interface_decls.append(decl)
            elif isinstance(decl, program.Service):
                service_decls.append(decl)
            elif isinstance(decl, program.Entry):
                assert not entry
                entry = decl
        if entry:
            entry_blocks.append(entry)

    for record in record_decls:
        attrs = []

        for decl in record.decls:
            if isinstance(decl, program.Attr):
                decl.type = decl.type.resolve_type(types)
                attrs.append((decl.name, decl.type))

        record.type = program_types.Record(record.name, attrs, {}, {})
        assert not record.name in types
        types[record.name] = record.type
        record.module_interface.types[record.name] = record.type

    for enum in enum_decls:
        enum.type = program_types.Enum(enum.name, {})
        types[enum.name] = enum.type
        enum.module_interface.types[enum.name] = enum.type

    for enum in enum_decls:
        for constructor in enum.constructors:
            constructor.resolve_types(types)
            assert not constructor.name in enum.type.constructors
            enum.type.constructors[constructor.name] = constructor.types
            signature = type_check_code_block.FunctionSignature(constructor.types, enum.type)
            enum.module_interface.signatures[constructor.name] = signature

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
                type_check_constructor(record.module_interface, dict(record.type.attrs), decl)
            elif isinstance(decl, program.Function):
                type_check_method(record.module_interface, record.type, dict(record.type.attrs), decl)

    for interface in interface_decls:
        methods = {}

        for decl in interface.decls:
            decl.resolve_types(types)
            methods[decl.name] = (decl.parameters, decl.return_type)

        interface.type = program_types.Interface(interface.name, methods)
        assert not interface.name in interface_types
        interface_types[interface.name] = interface.type
        interface.module_interface.interface_types[interface.name] = interface.type

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
        service.private_type = program_types.PrivateService(service.name, private_methods)
        services[service.name] = service.type
        service.module_interface.services[service.name] = service.type

    for function in function_decls:
        assert not function.name in function.module_interface.signatures
        function.resolve_types(types)
        signature = type_check_code_block.FunctionSignature(
                        function.parameter_types,
                        function.return_type
                    )
        function.module_interface.signatures[function.name] = signature

    for coroutine in coroutine_decls:
        assert not coroutine.name in coroutine.module_interface.signatures
        coroutine.resolve_types(types)
        arg_types = coroutine.parameter_types
        signature = type_check_code_block.CoroutineSignature(
                        coroutine.parameter_types,
                        coroutine.receive_type,
                        coroutine.yield_type
                    )
        coroutine.module_interface.signatures[coroutine.name] = signature

    for service in service_decls:
        all_attrs = service.type.all_attrs
        for service_decl in service.decls:
            if isinstance(service_decl, program.Implements):
                for method_decl in service_decl.decls:
                    type_check_method(service.module_interface, service.private_type, all_attrs, method_decl, True)
            elif isinstance(service_decl, program.Private):
                for private_decl in service_decl.decls:
                    type_check_method(service.module_interface, service.private_type, all_attrs, private_decl, True)
            elif isinstance(service_decl, program.Constructor):
                type_check_constructor(service.module_interface, attrs, service_decl)

    for function in function_decls:
        type_check_function(function)

    for coroutine in coroutine_decls:
        type_check_coroutine(coroutine)

    for entry in entry_blocks:
        context = type_check_code_block.TypeCheckingContext(module_interfaces, entry.module_interface, types, services, None, None, entry_point, {}, False, {})
        type_check_code_block.type_check_code_block(context, entry.body)
