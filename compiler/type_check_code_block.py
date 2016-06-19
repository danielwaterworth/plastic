import program
import program_types

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
    def __init__(self, signatures, types, services, receive_type, yield_type, return_type, attrs, attr_store, variable_types):
        self.signatures = signatures
        self.types = types
        self.services = services
        self.receive_type = receive_type
        self.yield_type = yield_type
        self.return_type = return_type
        self.attrs = attrs
        self.attr_store = attr_store
        self.variable_types = variable_types

    def add(self, name, type):
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
    'print_num': ([program_types.uint], program_types.void),
    'print_bool': ([program_types.bool], program_types.void),
    'print_byte': ([program_types.byte], program_types.void),
    'print_string': ([program_types.string], program_types.void)
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
arithmetic_operators = ['+', '-', '*', '/']

def operator_type(operator, rhs_type, lhs_type):
    if operator in comparison_operators:
        assert rhs_type == program_types.uint
        assert lhs_type == program_types.uint
        return program_types.bool
    elif operator in ['==', '!=']:
        assert lhs_type == program_types.uint
        assert rhs_type == program_types.uint
        if operator == '==':
            return program_types.bool
        else:
            return program_types.bool
    elif operator in arithmetic_operators:
        return program_types.uint
    else:
        raise NotImplementedError('unknown operator: %s' % operator)

def type_check_code_block(context, code_block):
    def infer_expression_type(expression):
        if isinstance(expression, program.Variable):
            expression.type = context.lookup(expression.name)
        elif isinstance(expression, program.ByteLiteral):
            expression.type = program_types.byte
        elif isinstance(expression, program.NumberLiteral):
            expression.type = program_types.uint
        elif isinstance(expression, program.BoolLiteral):
            expression.type = program_types.bool
        elif isinstance(expression, program.VoidLiteral):
            expression.type = program_types.void
        elif isinstance(expression, program.StringLiteral):
            expression.type = program_types.string
        elif isinstance(expression, program.AttrLoad):
            expression.type = context.lookup_attr(expression.attr)
        elif isinstance(expression, program.Yield):
            value_type = infer_expression_type(expression.value)
            assert value_type == context.yield_type
            expression.type = context.receive_type
        elif isinstance(expression, program.Run):
            coroutine = infer_expression_type(expression.coroutine)
            assert isinstance(coroutine, program_types.Coroutine)
            expression.type = coroutine.yield_type
        elif isinstance(expression, program.Resume):
            coroutine = infer_expression_type(expression.coroutine)
            value = infer_expression_type(expression.value)
            assert isinstance(coroutine, program_types.Coroutine)
            assert value == coroutine.receive_type
            expression.type = coroutine.yield_type
        elif isinstance(expression, program.IsDone):
            coroutine = infer_expression_type(expression.coroutine)
            assert isinstance(coroutine, program_types.Coroutine)
            expression.type = program_types.bool
        elif isinstance(expression, program.BinOp):
            rhs_type = infer_expression_type(expression.rhs)
            lhs_type = infer_expression_type(expression.lhs)
            expression.type = operator_type(expression.operator, rhs_type, lhs_type)
        elif isinstance(expression, program.FunctionCall):
            signature = context.signatures[expression.name]
            if isinstance(signature, FunctionSignature):
                argument_types = [infer_expression_type(argument) for argument in expression.arguments]
                return_type = signature.produce_return_type(argument_types)
                expression.coroutine_call = False
                expression.type = return_type
            elif isinstance(signature, CoroutineSignature):
                argument_types = [infer_expression_type(argument) for argument in expression.arguments]
                assert signature.parameter_types == argument_types
                expression.coroutine_call = True
                expression.type = program_types.Coroutine(signature.receive_type, signature.yield_type)
            else:
                raise NotImplementedError('not implemented signature type: %s' % type(signature))
        elif isinstance(expression, program.SysCall):
            expected_arg_types, return_type = sys_call_signatures[expression.name]
            argument_types = [infer_expression_type(argument) for argument in expression.arguments]
            assert expected_arg_types == argument_types
            expression.type = return_type
        elif isinstance(expression, program.MethodCall):
            object_type = infer_expression_type(expression.obj)
            expected_arg_types, return_type = object_type.method_signature(expression.name)
            argument_types = [infer_expression_type(argument) for argument in expression.arguments]
            assert expected_arg_types == argument_types
            expression.type = return_type
        elif isinstance(expression, program.ConstructorCall):
            record_type = context.types[expression.ty]
            expected_arg_types = record_type.constructor_signatures[expression.name]
            argument_types = [infer_expression_type(argument) for argument in expression.arguments]
            assert expected_arg_types == argument_types
            expression.type = record_type
        elif isinstance(expression, program.ServiceConstructorCall):
            service = context.services[expression.service]
            dependency_types = [infer_expression_type(argument) for argument in expression.service_arguments]
            assert len(dependency_types) == len(service.dependency_types)
            for service_arg, interface in zip(dependency_types, service.dependency_types):
                assert service_arg.is_subtype_of(interface)
            constructor_arg_types = [infer_expression_type(argument) for argument in expression.arguments]
            assert constructor_arg_types == service.constructor_signatures[expression.name]
            expression.type = service
        elif isinstance(expression, program.TupleConstructor):
            value_types = [infer_expression_type(value) for value in expression.values]
            expression.type = program_types.Tuple(value_types)
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
        elif isinstance(statement, program.Conditional):
            assert not statement.true_block.ret
            assert not statement.false_block.ret

            assert infer_expression_type(statement.expression) == program_types.bool

            before_context = context.copy_types()

            for true_statement in statement.true_block.statements:
                type_check_statement(true_statement)

            context.variable_types, after_true_context = before_context, context.variable_types

            for false_statement in statement.false_block.statements:
                type_check_statement(false_statement)

            context.variable_types = merge_contexts(context.variable_types, after_true_context)
        elif isinstance(statement, program.While):
            assert not statement.body.ret

            for body_statement in statement.body.statements:
                type_check_statement(body_statement)

            assert infer_expression_type(statement.expression) == program_types.bool
        elif isinstance(statement, program.Expression):
            infer_expression_type(statement)
        else:
            raise NotImplementedError('unknown statement type: %s' % type(statement))

    for statement in code_block.statements:
        type_check_statement(statement)

    if code_block.ret:
        return_type = infer_expression_type(code_block.ret.expression)
        if not return_type.is_subtype_of(context.return_type):
            raise TypeError('expected %s, but got %s' % (context.return_type, return_type))
