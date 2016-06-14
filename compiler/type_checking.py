import program
import program_types

sys_call_signatures = {
    'print_num': ([program_types.uint], program_types.void),
    'print_bool': ([program_types.bool], program_types.void)
}

class TypeCheckingContext(object):
    def __init__(self, return_type, types, attrs, attr_store):
        self.return_type = return_type
        self.types = types
        self.attrs = attrs
        self.attr_store = attr_store

    def add(self, name, type):
        if name in self.types:
            if self.types[name] != type:
                raise TypeError('expected %s to be %s instead of %s' % (name, self.types[name], type))
        else:
            self.types[name] = type

    def lookup(self, name):
        return self.types[name]

    def lookup_attr(self, name):
        return self.attrs[name]

    def copy_types(self):
        return dict(self.types)

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

def type_check(decls):
    function_signatures = {}
    types = {
        'UInt': program_types.uint,
        'Bool': program_types.bool,
        'Void': program_types.void,
        'Byte': program_types.byte
    }

    def resolve_type(t):
        return t.resolve_type(types)

    def type_check_code_block(context, code_block):
        def infer_expression_type(expression):
            if isinstance(expression, program.Variable):
                expression.type = context.lookup(expression.name)
            elif isinstance(expression, program.NumberLiteral):
                expression.type = program_types.uint
            elif isinstance(expression, program.BoolLiteral):
                expression.type = program_types.bool
            elif isinstance(expression, program.Load):
                assert infer_expression_type(expression.address) == program_types.uint
                expression.type = program_types.uint
            elif isinstance(expression, program.AttrLoad):
                expression.type = context.lookup_attr(expression.attr)
            elif isinstance(expression, program.BinOp):
                rhs_type = infer_expression_type(expression.rhs)
                lhs_type = infer_expression_type(expression.lhs)
                expression.type = operator_type(expression.operator, rhs_type, lhs_type)
            elif isinstance(expression, program.FunctionCall):
                expected_arg_types, return_type = function_signatures[expression.name]
                argument_types = [infer_expression_type(argument) for argument in expression.arguments]
                assert expected_arg_types == argument_types
                expression.type = return_type
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
                record_type = types[expression.ty]
                expected_arg_types = record_type.constructors[expression.name]
                argument_types = [infer_expression_type(argument) for argument in expression.arguments]
                assert expected_arg_types == argument_types
                expression.type = record_type
            else:
                raise NotImplementedError('unknown expression type: %s' % type(expression))
            return expression.type

        def type_check_statement(statement):
            if isinstance(statement, program.Assignment):
                expression_type = infer_expression_type(statement.expression)
                context.add(statement.name, expression_type)
            elif isinstance(statement, program.Store):
                address_type = infer_expression_type(statement.address)
                value_type = infer_expression_type(statement.value)
                assert address_type == program_types.uint
                assert value_type == program_types.uint
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

                context.types, after_true_context = before_context, context.types

                for false_statement in statement.false_block.statements:
                    type_check_statement(false_statement)

                context.types = merge_contexts(context.types, after_true_context)
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
            if context.return_type != return_type:
                raise TypeError('expected %s to equal %s' % (return_type, context.return_type))

    def type_check_function(function):
        context = TypeCheckingContext(function.return_type, dict(function.parameters), {}, False)

        type_check_code_block(context, function.body)

    def type_check_constructor(attr_types, constructor):
        context = TypeCheckingContext(program_types.void, dict(constructor.parameters), attr_types, True)

        type_check_code_block(context, constructor.body)

    def type_check_method(record_type, attr_types, method):
        scope = dict(method.parameters)
        scope['self'] = record_type
        context = TypeCheckingContext(method.return_type, scope, attr_types, False)

        type_check_code_block(context, method.body)

    functions = []
    records = []
    for decl in decls:
        if isinstance(decl, program.Function):
            functions.append(decl)
        elif isinstance(decl, program.Record):
            records.append(decl)

    for record in records:
        attrs = []

        for decl in record.decls:
            if isinstance(decl, program.Attr):
                decl.type = resolve_type(decl.type)
                attrs.append((decl.name, decl.type))

        record.type = program_types.Record(record.name, attrs, {}, {})
        assert not record.name in types
        types[record.name] = record.type

    for record in records:
        constructors = record.type.constructors
        methods = record.type.methods

        for decl in record.decls:
            if isinstance(decl, program.Constructor):
                decl.parameters = [(name, resolve_type(t)) for name, t in decl.parameters]
                parameter_types = [param[1] for param in decl.parameters]
                constructors[decl.name] = parameter_types
            elif isinstance(decl, program.Method):
                decl.parameters = [(name, resolve_type(t)) for name, t in decl.parameters]
                parameter_types = [param[1] for param in decl.parameters]
                decl.return_type = resolve_type(decl.return_type)
                methods[decl.name] = (parameter_types, decl.return_type)

    for record in records:
        for decl in record.decls:
            if isinstance(decl, program.Constructor):
                type_check_constructor(dict(record.type.attrs), decl)
            elif isinstance(decl, program.Method):
                type_check_method(record.type, dict(record.type.attrs), decl)

    for function in functions:
        assert not function.name in function_signatures
        function.parameters = [(name, resolve_type(t)) for name, t in function.parameters]
        arg_types = [arg[1] for arg in function.parameters]
        function.return_type = resolve_type(function.return_type)
        function_signatures[function.name] = (arg_types, function.return_type)

    for function in functions:
        type_check_function(function)
