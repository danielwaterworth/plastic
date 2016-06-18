import ply.yacc as yacc

from lexer import tokens
import program
import program_types

def p_program_empty(p):
    '''program : empty'''
    p[0] = []

def p_program(p):
    '''program : program top_level_decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_function(p):
    '''top_level_decl : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS ARROW type DO code_block END'''
    p[0] = program.Function(p[2], p[4], p[7], p[9])

def p_record(p):
    '''top_level_decl : RECORD UPPER_NAME record_decl_list END'''
    p[0] = program.Record(p[2], p[3])

def p_interface(p):
    '''top_level_decl : INTERFACE UPPER_NAME interface_decl_list END'''
    p[0] = program.Interface(p[2], p[3])

def p_service(p):
    '''top_level_decl : SERVICE UPPER_NAME OPEN_PARENS dependencies CLOSE_PARENS service_decl_list END'''
    p[0] = program.Service(p[2], p[4], p[6])

def p_entry(p):
    '''top_level_decl : ENTRY code_block END'''
    p[0] = program.Entry(p[2])

def p_dependencies_empty(p):
    '''dependencies : empty'''
    p[0] = []

def p_dependencies(p):
    '''dependencies : non_empty_dependencies'''
    p[0] = p[1]

def p_non_empty_dependencies_initial(p):
    '''non_empty_dependencies : dependency'''
    p[0] = [p[1]]

def p_non_empty_dependencies(p):
    '''non_empty_dependencies : non_empty_dependencies COMMA dependency'''
    p[1].append(p[3])
    p[0] = p[1]

def p_dependency(p):
    '''dependency : LOWER_NAME COLON UPPER_NAME'''
    p[0] = (p[1], p[3])

def p_parameter_list_empty(p):
    '''parameter_list : empty'''
    p[0] = []

def p_parameter_list(p):
    '''parameter_list : non_empty_parameter_list'''
    p[0] = p[1]

def p_non_empty_parameter_list_initial(p):
    '''non_empty_parameter_list : parameter'''
    p[0] = [p[1]]

def p_non_empty_parameter_list(p):
    '''non_empty_parameter_list : non_empty_parameter_list COMMA parameter'''
    p[1].append(p[3])
    p[0] = p[1]

def p_parameter(p):
    '''parameter : LOWER_NAME COLON type'''
    p[0] = (p[1], p[3])

def p_record_decl_list_empty(p):
    '''record_decl_list : empty'''
    p[0] = []

def p_record_decl_list(p):
    '''record_decl_list : record_decl_list record_decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_attr(p):
    '''record_decl : ATTR LOWER_NAME COLON type SEMICOLON'''
    p[0] = program.Attr(p[2], p[4])

def p_record_constructor(p):
    '''record_decl : CONSTRUCTOR LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS code_block END'''
    p[0] = program.Constructor(p[2], p[4], p[6])

def p_record_method(p):
    '''record_decl : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS ARROW type DO code_block END'''
    p[0] = program.Function(p[2], p[4], p[7], p[9])

def p_interface_decl_list_empty(p):
    '''interface_decl_list : empty'''
    p[0] = []

def p_interface_decl_list(p):
    '''interface_decl_list : interface_decl_list interface_decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_interface_decl(p):
    '''interface_decl : LOWER_NAME OPEN_PARENS type_list CLOSE_PARENS ARROW type SEMICOLON'''
    p[0] = program.MethodSignature(p[1], p[3], p[6])

def p_service_decl_list_empty(p):
    '''service_decl_list : empty'''
    p[0] = []

def p_service_decl_list(p):
    '''service_decl_list : service_decl_list service_decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_service_decl_attr(p):
    '''service_decl : ATTR LOWER_NAME COLON type SEMICOLON'''
    p[0] = program.Attr(p[2], p[4])

def p_service_decl_constructor(p):
    '''service_decl : CONSTRUCTOR LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS code_block END'''
    p[0] = program.Constructor(p[2], p[4], p[6])

def p_service_decl_private(p):
    '''service_decl : PRIVATE service_method_list END'''
    p[0] = program.Private(p[2])

def p_service_decl_implements(p):
    '''service_decl : IMPLEMENTS UPPER_NAME service_method_list END'''
    p[0] = program.Implements(p[2], p[3])

def p_service_method_list_empty(p):
    '''service_method_list : empty'''
    p[0] = []

def p_service_method_list(p):
    '''service_method_list : service_method_list service_method'''
    p[1].append(p[2])
    p[0] = p[1]

def p_service_method(p):
    '''service_method : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS ARROW type DO code_block END'''
    p[0] = program.Function(p[2], p[4], p[7], p[9])

def p_type_named(p):
    '''type : UPPER_NAME'''
    p[0] = program_types.NamedType(p[1])

def p_type_array(p):
    '''type : type OPEN_SQUARE NUMBER CLOSE_SQUARE'''
    p[0] = program_types.Array(p[1], int(p[3]))

def p_type_tuple(p):
    '''type : OPEN_PARENS type_list CLOSE_PARENS'''
    p[0] = program_types.Tuple(p[2])

def p_empty_type_list(p):
    '''type_list : empty'''
    p[0] = []

def p_non_empty_type_list(p):
    '''type_list : non_empty_type_list'''
    p[0] = p[1]

def p_type_list_initial(p):
    '''non_empty_type_list : type'''
    p[0] = [p[1]]

def p_type_list(p):
    '''non_empty_type_list : non_empty_type_list COMMA type'''
    p[1].append(p[3])
    p[0] = p[1]

def p_code_block(p):
    '''code_block : statement_list block_end'''
    p[0] = program.CodeBlock(p[1], p[2])

def p_statement_list_empty(p):
    '''statement_list : empty'''
    p[0] = []

def p_statement_list(p):
    '''statement_list : statement_list statement'''
    p[1].append(p[2])
    p[0] = p[1]

def p_function_call(p):
    '''function_call : OPEN_PARENS argument_list CLOSE_PARENS'''
    p[0] = p[2]

def p_argument_list_empty(p):
    '''argument_list : empty'''
    p[0] = []

def p_argument_list(p):
    '''argument_list : non_empty_argument_list'''
    p[0] = p[1]

def p_non_empty_argument_list_initial(p):
    '''non_empty_argument_list : expression'''
    p[0] = [p[1]]

def p_non_empty_argument_list(p):
    '''non_empty_argument_list : non_empty_argument_list COMMA expression'''
    p[1].append(p[3])
    p[0] = p[1]

def p_function_call_statement(p):
    '''statement : expression SEMICOLON'''
    p[0] = p[1]

def p_assignment_statement(p):
    '''statement : LOWER_NAME ASSIGNMENT expression SEMICOLON'''
    p[0] = program.Assignment(p[1], p[3])

def p_attr_assignment(p):
    '''statement : ATTR LOWER_NAME ASSIGNMENT expression SEMICOLON'''
    p[0] = program.AttrStore(p[2], p[4])

def p_conditional(p):
    '''statement : IF OPEN_PARENS expression CLOSE_PARENS code_block ELSE code_block END'''
    p[0] = program.Conditional(p[3], p[5], p[7])

def p_while(p):
    '''statement : DO code_block WHILE OPEN_PARENS expression CLOSE_PARENS'''
    p[0] = program.While(p[2], p[5])

def p_expression_variable(p):
    '''expression : LOWER_NAME'''
    p[0] = program.Variable(p[1])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = program.NumberLiteral(int(p[1]))

def p_expression_true(p):
    '''expression : TRUE'''
    p[0] = program.BoolLiteral(True)

def p_expression_false(p):
    '''expression : FALSE'''
    p[0] = program.BoolLiteral(False)

def p_expression_void(p):
    '''expression : VOID'''
    p[0] = program.VoidLiteral()

def p_expression_sys_call(p):
    '''expression : SYS LOWER_NAME function_call'''
    p[0] = program.SysCall(p[2], p[3])

def p_expression_call(p):
    '''expression : LOWER_NAME function_call'''
    p[0] = program.FunctionCall(p[1], p[2])

def p_expression_constructor(p):
    '''expression : UPPER_NAME DOT LOWER_NAME function_call'''
    p[0] = program.ConstructorCall(p[1], p[3], p[4])

def p_expression_service_constructor(p):
    '''expression : UPPER_NAME function_call DOT LOWER_NAME function_call'''
    p[0] = program.ServiceConstructorCall(p[1], p[2], p[4], p[5])

def p_expression_attr(p):
    '''expression : ATTR LOWER_NAME'''
    p[0] = program.AttrLoad(p[2])

def p_bracketed_expr(p):
    '''expression : OPEN_PARENS expression CLOSE_PARENS'''
    p[0] = p[2]

precedence = (
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIV'),
    ('right', 'ATTR'),
    ('right', 'DOT')
)

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MUL expression
                  | expression DIV expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression
                  | expression EQ expression
                  | expression NE expression'''
    p[0] = program.BinOp(p[1], p[3], p[2])

def p_method_call_expression(p):
    '''expression : expression DOT LOWER_NAME function_call'''
    p[0] = program.MethodCall(p[1], p[3], p[4])

def p_return(p):
    '''block_end : RETURN expression SEMICOLON'''
    p[0] = program.Return(p[2])

def p_end(p):
    '''block_end : empty'''
    p[0] = None

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    print p
    raise Exception("Syntax error in input!")

parser = yacc.yacc()
