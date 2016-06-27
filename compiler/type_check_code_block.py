import program
import program_types
from program_types import bool, uint, string, char, byte, bytestring, socket
from program_types import void, file

class Call(object):
    pass

class FunctionCall(Call):
    def __init__(self, module):
        self.module = module

class MethodCall(Call):
    def __init__(self, obj):
        self.obj = obj

class RecordConstructorCall(Call):
    def __init__(self, module, record):
        self.module = module
        self.record = record

class ServiceConstructorCall(Call):
    def __init__(self, module, service, dependencies):
        self.module = module
        self.service = service
        self.dependencies = dependencies

    def evaluate(self, context, function, arguments):
        service_arguments = [arg.evaluate(context) for arg in self.dependencies]
        arguments = [arg.evaluate(context) for arg in arguments]
        return context.service(self.service, service_arguments, function, arguments)

class Signature(object):
    pass

class CoroutineSignature(Signature):
    def __init__(self, parameter_types, receive_type, yield_type):
        self.parameter_types = parameter_types
        self.receive_type = receive_type
        self.yield_type = yield_type

class FunctionSignature(Signature):
    def __init__(self, parameter_types, return_type):
        self.parameter_types = parameter_types
        self.return_type = return_type

    def produce_return_type(self, argument_types):
        assert len(self.parameter_types) == len(argument_types)

        quantified = {}
        for parameter, argument in zip(self.parameter_types, argument_types):
            parameter.match(quantified, argument)

        return self.return_type.template(quantified)

class TypeCheckingContext(object):
    def __init__(self, module_interfaces, current_module, receive_type, yield_type, return_type, attrs, attr_store, variable_types):
        self.module_interfaces = module_interfaces
        self.current_module = current_module
        self.receive_type = receive_type
        self.yield_type = yield_type
        self.return_type = return_type
        self.attrs = attrs
        self.attr_store = attr_store
        self.variable_types = variable_types

    def add(self, name, type):
        if name in self.current_module.imports:
            raise Exception('variable name shadows import')

        if name in self.variable_types:
            if self.variable_types[name] != type:
                raise TypeError('expected %s to be %s instead of %s' % (name, self.variable_types[name], type))
        else:
            self.variable_types[name] = type

    def lookup(self, name):
        return self.variable_types[name]

    def lookup_attr(self, name):
        return self.attrs[name]

    def copy_types(self):
        return dict(self.variable_types)

sys_call_signatures = {
    'print_uint': ([uint], void),
    'print_bool': ([bool], void),
    'print_char': ([char], void),
    'print_string': ([string], void),

    'socket_socket': ([uint, uint, uint], socket),
    'socket_bind': ([socket, string, uint], void),
    'socket_listen': ([socket, uint], void),
    'socket_accept': ([socket], socket),
    'socket_recv': ([socket, uint], bytestring),
    'socket_send': ([socket, bytestring], void),
    'socket_close': ([socket], void),

    'file_open': ([bytestring, uint], file),
    'file_read': ([file, uint], bytestring),
    'file_write': ([file, bytestring], void),
    'file_close': ([file], void),
}

op_call_signatures = {
    "EPOLLIN" : ([], uint),
    "EPOLLOUT": ([], uint),
    "unpack_uint": ([bytestring], uint),
}

def merge_contexts(a, b):
    types = {}
    for name in set(a) & set(b):
        a_type = a[name]
        b_type = b[name]
        if a_type != b_type:
            raise TypeError('%s receives different types, %s and %s, in the branchs of a conditional' % (name, a_type, b_type))
        types[name] = a_type
    return types

comparison_operators = ['<', '>', '<=', '>=']
arithmetic_operators = ['-', '*', '/']
logical_operators = ['and', 'or']
equality_types = [
    uint,
    bool,
    byte,
    bytestring,
    string,
    char,
]

def operator_type(operator, rhs_type, lhs_type):
    if operator in logical_operators:
        assert rhs_type == bool
        assert rhs_type == bool
        return bool
    elif operator in comparison_operators:
        assert rhs_type == uint
        assert lhs_type == uint
        return bool
    elif operator in ['==', '!=']:
        assert lhs_type == rhs_type
        if not lhs_type in equality_types:
            raise Exception("%s doesn't have equality" % type(lhs_type))
        return bool
    elif operator == '+':
        assert lhs_type == rhs_type
        assert lhs_type in [uint, string]
        return lhs_type
    elif operator in arithmetic_operators:
        assert lhs_type == uint
        assert rhs_type == uint
        return uint
    else:
        raise NotImplementedError('unknown operator: %s' % operator)

def type_check_code_block(context, code_block):
    def infer_expression_type(expression):
        if isinstance(expression, program.Variable):
            expression.type = context.lookup(expression.name)
        elif isinstance(expression, program.TypeName):
            raise Exception('naked type name')
        elif isinstance(expression, program.TypeAccess):
            raise Exception('naked type access')
        elif isinstance(expression, program.CharLiteral):
            expression.type = char
        elif isinstance(expression, program.NumberLiteral):
            expression.type = uint
        elif isinstance(expression, program.BoolLiteral):
            expression.type = bool
        elif isinstance(expression, program.VoidLiteral):
            expression.type = void
        elif isinstance(expression, program.StringLiteral):
            expression.type = string
        elif isinstance(expression, program.AttrLoad):
            expression.type = context.lookup_attr(expression.attr)
        elif isinstance(expression, program.Yield):
            value_type = infer_expression_type(expression.value)
            assert value_type == context.yield_type
            expression.type = context.receive_type
        elif isinstance(expression, program.Run):
            coroutine = infer_expression_type(expression.coroutine)
            assert isinstance(coroutine, program_types.Instantiation)
            assert coroutine.constructor == program_types.coroutine
            assert len(coroutine.types) == 2
            expression.type = coroutine.types[1]
        elif isinstance(expression, program.Resume):
            coroutine = infer_expression_type(expression.coroutine)
            value = infer_expression_type(expression.value)
            assert isinstance(coroutine, program_types.Instantiation)
            assert coroutine.constructor == program_types.coroutine
            assert len(coroutine.types) == 2
            assert value == coroutine.types[0]
            expression.type = coroutine.types[1]
        elif isinstance(expression, program.IsDone):
            coroutine = infer_expression_type(expression.coroutine)
            assert isinstance(coroutine, program_types.Instantiation)
            assert coroutine.constructor == program_types.coroutine
            assert len(coroutine.types) == 2
            expression.type = bool
        elif isinstance(expression, program.Not):
            expression_type = infer_expression_type(expression.expression)
            assert expression_type == bool
            expression.type = bool
        elif isinstance(expression, program.BinOp):
            rhs_type = infer_expression_type(expression.rhs)
            lhs_type = infer_expression_type(expression.lhs)
            expression.type = operator_type(expression.operator, rhs_type, lhs_type)
        elif isinstance(expression, program.Call):
            argument_types = [infer_expression_type(argument) for argument in expression.arguments]

            if isinstance(expression.function, program.Variable):
                expression.call = FunctionCall(context.current_module)
                expression.function_name = expression.function.name
            elif isinstance(expression.function, program.RecordAccess):
                obj = expression.function.obj
                expression.function_name = expression.function.name
                if isinstance(obj, program.Variable) and obj.name in context.current_module.imports:
                    expression.call = FunctionCall(context.module_interfaces[obj.name])
                elif isinstance(obj, program.TypeName):
                    expression.call = RecordConstructorCall(context.current_module, obj.name)
                elif isinstance(obj, program.Call):
                    if isinstance(obj.function, program.TypeName):
                        expression.call = ServiceConstructorCall(context.current_module, obj.function.name, obj.arguments)
                    elif isinstance(obj.function, program.TypeAccess):
                        assert isinstance(obj.function.obj, program.Variable)
                        module = context.module_interfaces[obj.function.obj.name]
                        expression.call = ServiceConstructorCall(module, obj.function.name, obj.arguments)
                    else:
                        expression.call = MethodCall(obj)
                elif isinstance(obj, program.TypeAccess):
                    assert isinstance(obj.obj, program.Variable)
                    module = context.module_interfaces[obj.obj.name]
                    expression.call = RecordConstructorCall(module, obj.name)
                else:
                    expression.call = MethodCall(obj)
            else:
                raise NotImplementedError('unsupported type of call')

            function = expression.function_name
            if isinstance(expression.call, FunctionCall):
                signature = expression.call.module.signatures[function]
                if isinstance(signature, FunctionSignature):
                    expression.call.coroutine_call = False
                    expression.type = signature.produce_return_type(argument_types)
                elif isinstance(signature, CoroutineSignature):
                    assert signature.parameter_types == argument_types
                    expression.call.coroutine_call = True
                    expression.type = program_types.coroutine_type(signature.receive_type, signature.yield_type)
                else:
                    raise NotImplementedError('not implemented signature type: %s' % type(signature))
            elif isinstance(expression.call, MethodCall):
                object_type = infer_expression_type(expression.call.obj)
                expected_arg_types, return_type = object_type.method_signature(function)
                assert expected_arg_types == argument_types
                expression.type = return_type
            elif isinstance(expression.call, RecordConstructorCall):
                record_type = expression.call.module.types[expression.call.record]
                assert isinstance(record_type, program_types.Instantiation)
                assert isinstance(record_type.constructor, program_types.Record)
                expected_arg_types = record_type.constructor.constructor_signatures[function]
                assert expected_arg_types == argument_types
                expression.type = record_type
            elif isinstance(expression.call, ServiceConstructorCall):
                service = expression.call.module.services[expression.call.service]
                dependency_types = [infer_expression_type(argument) for argument in expression.call.dependencies]
                assert len(dependency_types) == len(service.dependency_types)
                for service_arg, interface in zip(dependency_types, service.dependency_types):
                    assert service_arg.is_subtype_of(interface)
                assert argument_types == service.constructor_signatures[function]
                expression.type = service
        elif isinstance(expression, program.RecordAccess):
            raise Exception('naked record access')
        elif isinstance(expression, program.SysCall):
            expected_arg_types, return_type = sys_call_signatures[expression.name]
            argument_types = [infer_expression_type(argument) for argument in expression.arguments]
            assert expected_arg_types == argument_types
            expression.type = return_type
        elif isinstance(expression, program.OpCall):
            expected_arg_types, return_type = op_call_signatures[expression.name]
            argument_types = [infer_expression_type(argument) for argument in expression.arguments]
            assert expected_arg_types == argument_types
            expression.type = return_type
        elif isinstance(expression, program.TupleConstructor):
            value_types = [infer_expression_type(value) for value in expression.values]
            expression.type = program_types.Instantiation(program_types.tuple, value_types)
        else:
            raise NotImplementedError('unknown expression type: %s' % type(expression))
        return expression.type

    def type_check_statement(statement):
        if isinstance(statement, program.Assignment):
            expression_type = infer_expression_type(statement.expression)
            context.add(statement.name, expression_type)
        elif isinstance(statement, program.AttrStore):
            if not context.attr_store:
                raise Exception('Attributes cannot be stored in this context')
            expected_type = context.lookup_attr(statement.attr)
            actual_type = infer_expression_type(statement.value)
            if expected_type != actual_type:
                raise TypeError('expected %s to equal %s' % (actual_type, expected_type))
        elif isinstance(statement, program.TupleDestructure):
            expression_type = infer_expression_type(statement.expression)
            assert isinstance(expression_type, program_types.Instantiation)
            assert expression_type.constructor == program_types.tuple
            assert len(statement.names) == len(expression_type.types)
            for name, t in zip(statement.names, expression_type.types):
                context.add(name, t)
        elif isinstance(statement, program.Conditional):
            assert infer_expression_type(statement.expression) == bool

            before_context = context.copy_types()

            for true_statement in statement.true_block.statements:
                type_check_statement(true_statement)
            type_check_terminator(statement.true_block.terminator)

            context.variable_types, after_true_context = before_context, context.variable_types

            for false_statement in statement.false_block.statements:
                type_check_statement(false_statement)
            type_check_terminator(statement.false_block.terminator)

            if not statement.true_block.terminator and not statement.false_block.terminator:
                context.variable_types = merge_contexts(context.variable_types, after_true_context)
            elif not statement.true_block.terminator:
                context.variable_types = after_true_context
            elif not statement.false_block.terminator:
                pass
            else:
                # Both branches terminated, nothing is in scope
                context.variable_types = {}
        elif isinstance(statement, program.While):
            assert not statement.body.terminator

            for body_statement in statement.body.statements:
                type_check_statement(body_statement)

            assert infer_expression_type(statement.expression) == bool
        elif isinstance(statement, program.Match):
            enum_type = infer_expression_type(statement.expression)
            assert isinstance(enum_type, program_types.Instantiation)
            assert isinstance(enum_type.constructor, program_types.Enum)
            constructors = enum_type.constructor.constructors

            before_context = context.copy_types()

            after_contexts = []

            generated_constructors = set()
            for clause in statement.clauses:
                assert not clause.name in generated_constructors
                arg_types = constructors[clause.name]
                generated_constructors.add(clause.name)
                assert len(arg_types) == len(clause.parameters)

                for name, t in zip(clause.parameters, arg_types):
                    context.add(name, t)

                for clause_statement in clause.block.statements:
                    type_check_statement(clause_statement)

                if clause.block.terminator:
                    type_check_terminator(clause.block.terminator)
                else:
                    after_contexts.append(context.variable_types)

                context.variable_types = dict(before_context)

            assert generated_constructors == set(constructors)
            if after_contexts:
                context.variable_types = reduce(merge_contexts, after_contexts)
            else:
                context.variable_types = {}
        elif isinstance(statement, program.Debug):
            expression = infer_expression_type(statement.expression)
            assert expression == string
        elif isinstance(statement, program.Expression):
            infer_expression_type(statement)
        else:
            raise NotImplementedError('unknown statement type: %s' % type(statement))

    def type_check_terminator(terminator):
        if terminator:
            if isinstance(terminator, program.Return):
                return_type = infer_expression_type(terminator.expression)
                if not return_type.is_subtype_of(context.return_type):
                    raise TypeError('expected %s, but got %s' % (context.return_type, return_type))
            elif isinstance(terminator, program.Throw):
                exception_type = infer_expression_type(terminator.exception)
            else:
                raise NotImplementedError()

    for statement in code_block.statements:
        type_check_statement(statement)

    type_check_terminator(code_block.terminator)
