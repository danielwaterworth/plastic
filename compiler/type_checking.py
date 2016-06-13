import program

sys_call_signatures = {
    'print_num': ([program.uint], program.void)
}

class TypeCheckingContext(object):
    def __init__(self, function_name, types):
        self.function_name = function_name
        self.types = types

    def add(self, name, type):
        if name in self.types:
            if self.types[name] != type:
                raise TypeError('expected %s to be %s instead of %s' % (name, self.types[name], type))
        else:
            self.types[name] = type

    def lookup(self, name):
        return self.types[name]

    def copy_types(self):
        return dict(self.types)

def merge_contexts(a, b):
    types = {}
    for name in set(a) & set(b):
        a_type = a.types[name]
        b_type = b.types[name]
        if a_type != b_type:
            raise TypeError('%s receives different types, %s and %s, in the branchs of a conditional' % (name, a_type, b_type))
        types[name] = a_type
    return types

comparison_operators = ['<', '>', '<=', '>=']
arithmetic_operators = ['+', '-', '*', '/']

def operator_type(operator, rhs_type, lhs_type):
    if operator in comparison_operators:
        assert rhs_type == program.uint
        assert lhs_type == program.uint
        return program.bool
    elif operator in ['==', '!=']:
        assert lhs_type == program.uint
        assert rhs_type == program.uint
        if operator == '==':
            return program.bool
        else:
            return program.bool
    elif operator in arithmetic_operators:
        return program.uint
    else:
        raise NotImplementedError('unknown operator: %s' % operator)

def type_check(functions):
    function_signatures = {}

    def type_check_function(function):
        context = TypeCheckingContext(function.name, dict(function.parameters))

        def infer_expression_type(expression):
            if isinstance(expression, program.Variable):
                return context.lookup(expression.name)
            elif isinstance(expression, program.NumberLiteral):
                return program.uint
            elif isinstance(expression, program.BoolLiteral):
                return program.bool
            elif isinstance(expression, program.Load):
                assert infer_expression_type(expression.address) == program.uint
                return program.uint
            elif isinstance(expression, program.BinOp):
                rhs_type = infer_expression_type(expression.rhs)
                lhs_type = infer_expression_type(expression.lhs)
                return operator_type(expression.operator, rhs_type, lhs_type)
            else:
                raise NotImplementedError('unknown expression type: %s' % type(expression))

        def type_check_statement(statement):
            if isinstance(statement, program.Assignment):
                expression_type = infer_expression_type(statement.expression)
                context.add(statement.name, expression_type)
            elif isinstance(statement, program.FunctionCallStatement):
                expected_arg_types, return_type = function_signatures[statement.name]
                argument_types = [infer_expression_type(argument) for argument in statement.arguments]
                assert argument_types == expected_arg_types
            elif isinstance(statement, program.SysCallStatement):
                expected_arg_types, return_type = sys_call_signatures[statement.name]
                argument_types = [infer_expression_type(argument) for argument in statement.arguments]
                assert argument_types == expected_arg_types
            elif isinstance(statement, program.Store):
                address_type = infer_expression_type(statement.address)
                value_type = infer_expression_type(statement.value)
                assert address_type == program.uint
                assert value_type == program.uint
            elif isinstance(statement, program.Conditional):
                assert not statement.true_block.ret
                assert not statement.false_block.ret

                assert infer_expression_type(statement.expression) == program.bool

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

                assert infer_expression_type(statement.expression) == program.bool
            else:
                raise NotImplementedError('unknown statement type: %s' % type(statement))

        for statement in function.body.statements:
            type_check_statement(statement)

        if function.body.ret:
            return_type = infer_expression_type(function.body.ret.expression)
            assert return_type == function.return_type

    for function in functions:
        assert not function.name in function_signatures
        arg_types = [arg[1] for arg in function.parameters]
        function_signatures[function.name] = (arg_types, function.return_type)

    for function in functions:
        type_check_function(function)
