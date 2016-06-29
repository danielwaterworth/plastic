import program
import type_check_code_block
import module_interface
import program_types
from program_types import bool, uint, string, char, byte, bytestring, socket
from program_types import void, file

primitives = {
    'UInt': uint,
    'Bool': bool,
    'Void': void,
    'Byte': byte,
    'ByteString': bytestring,
    'Char': char,
    'String': string,
    'Socket': socket,
    'File': file,
}
entry_point = program_types.Interface('EntryPoint', {'main': ([], bool)})
builtin_interfaces = {'EntryPoint': entry_point}

def type_check_module(module_interfaces, module_name, module_decl):
    module = module_interface.ModuleInterface(module_name, module_decl.imports)
    module_interfaces[module_name] = module

    def type_check_function(function):
        context = type_check_code_block.TypeCheckingContext(
                        module_interfaces,
                        module,
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
                        module,
                        coroutine.receive_type,
                        coroutine.yield_type,
                        void,
                        {},
                        False,
                        dict(coroutine.parameters)
                    )

        type_check_code_block.type_check_code_block(context, coroutine.body)

    def type_check_constructor(attr_types, constructor):
        context = type_check_code_block.TypeCheckingContext(
                        module_interfaces,
                        module,
                        None,
                        None,
                        void,
                        attr_types,
                        True,
                        dict(constructor.parameters)
                    )

        type_check_code_block.type_check_code_block(context, constructor.body)

    def type_check_method(self_type, attr_types, method, store_attributes=False):
        scope = dict(method.parameters)
        scope['self'] = self_type
        context = type_check_code_block.TypeCheckingContext(
                        module_interfaces,
                        module,
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
    entry = None

    for decl in module_decl.decls:
        decl.module_interface = module
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

    for record in record_decls:
        attrs = []

        types = {}
        types.update(primitives)
        types.update(module.types)

        for decl in record.decls:
            if isinstance(decl, program.Attr):
                decl.type = decl.type.resolve_type(module_interfaces, types)
                attrs.append((decl.name, decl.type))

        record.type_constructor = program_types.Record(record.name, attrs, {}, {})
        record.type = program_types.Instantiation(record.type_constructor, [])
        assert not record.name in types
        module.types[record.name] = record.type

    for enum in enum_decls:
        enum.type_constructor = program_types.Enum(enum.name, {})
        enum.type = program_types.Instantiation(enum.type_constructor, [])
        module.types[enum.name] = enum.type

    for enum in enum_decls:
        types = {}
        types.update(primitives)
        types.update(module.types)

        for constructor in enum.constructors:
            constructor.resolve_types(module_interfaces, types)
            assert not constructor.name in enum.type_constructor.constructors
            enum.type_constructor.constructors[constructor.name] = constructor.types
            signature = type_check_code_block.FunctionSignature(constructor.types, enum.type)
            module.signatures[constructor.name] = signature

    for record in record_decls:
        types = {}
        types.update(primitives)
        types.update(module.types)

        constructor_signatures = record.type_constructor.constructor_signatures
        methods = record.type_constructor.methods

        for decl in record.decls:
            if isinstance(decl, program.Constructor):
                decl.resolve_types(module_interfaces, types)
                constructor_signatures[decl.name] = decl.parameter_types
            elif isinstance(decl, program.Function):
                decl.resolve_types(module_interfaces, types)
                methods[decl.name] = decl.signature

    for record in record_decls:
        for decl in record.decls:
            if isinstance(decl, program.Constructor):
                type_check_constructor(dict(record.type_constructor.attrs), decl)
            elif isinstance(decl, program.Function):
                type_check_method(record.type, dict(record.type_constructor.attrs), decl)

    for interface in interface_decls:
        types = {}
        types.update(primitives)
        types.update(module.types)

        methods = {}

        for decl in interface.decls:
            decl.resolve_types(module_interfaces, types)
            methods[decl.name] = (decl.parameters, decl.return_type)

        interface.type_constructor = program_types.Interface(interface.name, methods)
        assert not interface.name in builtin_interfaces
        assert not interface.name in module.interface_types
        module.interface_types[interface.name] = interface.type_constructor

    for service in service_decls:
        types = {}
        types.update(primitives)
        types.update(module.types)

        interface_types = {}
        interface_types.update(builtin_interfaces)
        interface_types.update(module.interface_types)

        attrs = {}
        dependency_names = {name for name, interface_name in service.dependencies}
        dependencies = [(name, interface.resolve_interface(module_interfaces, interface_types)) for name, interface in service.dependencies]
        constructor_signatures = {}
        interfaces = list()
        private_methods = {}

        for service_decl in service.decls:
            if isinstance(service_decl, program.Attr):
                service_decl.type = service_decl.type.resolve_type(module_interfaces, types)
                assert not service_decl.name in attrs
                assert not service_decl.name in dependency_names
                attrs[service_decl.name] = service_decl.type
            elif isinstance(service_decl, program.Implements):
                interface = service_decl.interface.resolve_interface(module_interfaces, interface_types)
                methods = {}

                for method_decl in service_decl.decls:
                    method_decl.resolve_types(module_interfaces, types)
                    methods[method_decl.name] = method_decl.signature

                assert methods == interface.constructor.methods
                interfaces.append(interface)
            elif isinstance(service_decl, program.Private):
                for private_decl in service_decl.decls:
                    private_decl.resolve_types(module_interfaces, types)
                    private_methods[private_decl.name] = private_decl.signature
            elif isinstance(service_decl, program.Constructor):
                service_decl.resolve_types(module_interfaces, types)
                constructor_signatures[service_decl.name] = service_decl.parameter_types
        service.type = program_types.Service(service.name, dependencies, attrs, constructor_signatures, interfaces)
        service.private_type = program_types.PrivateService(service.name, private_methods)
        module.services[service.name] = service.type

    for function in function_decls:
        types = {}
        types.update(primitives)
        types.update(module.types)

        assert not function.name in module.signatures
        function.resolve_types(module_interfaces, types)
        signature = type_check_code_block.FunctionSignature(
                        function.parameter_types,
                        function.return_type
                    )
        module.signatures[function.name] = signature

    for coroutine in coroutine_decls:
        types = {}
        types.update(primitives)
        types.update(module.types)

        assert not coroutine.name in module.signatures
        coroutine.resolve_types(module_interfaces, types)
        arg_types = coroutine.parameter_types
        signature = type_check_code_block.CoroutineSignature(
                        coroutine.parameter_types,
                        coroutine.receive_type,
                        coroutine.yield_type
                    )
        module.signatures[coroutine.name] = signature

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
        entry_point_type = program_types.Instantiation(entry_point, [])
        context = type_check_code_block.TypeCheckingContext(module_interfaces, module, None, None, entry_point_type, {}, False, {})
        type_check_code_block.type_check_code_block(context, entry.body)
