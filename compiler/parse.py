import ply.yacc as yacc

from lexer import tokens
import program
import program_types

def p_program_empty(p):
    '''program : imports top_level_decls'''
    p[0] = program.Program(p[1], p[2])

def p_imports_empty(p):
    '''imports : empty'''
    p[0] = []

def p_imports(p):
    '''imports : imports import_decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_import(p):
    '''import_decl : IMPORT LOWER_NAME'''
    p[0] = p[2]

def p_top_level_decls_empty(p):
    '''top_level_decls : empty'''
    p[0] = []

def p_top_level_decls(p):
    '''top_level_decls : top_level_decls top_level_decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_top_level_function(p):
    '''top_level_decl : function'''
    p[0] = p[1]

def p_top_level_coroutine(p):
    '''top_level_decl : coroutine'''
    p[0] = p[1]

def p_record(p):
    '''top_level_decl : RECORD UPPER_NAME record_decl_list END'''
    p[0] = program.Record(p[2], p[3])

def p_enum(p):
    '''top_level_decl : ENUM UPPER_NAME enum_constructors END'''
    p[0] = program.Enum(p[2], p[3])

def p_interface(p):
    '''top_level_decl : INTERFACE UPPER_NAME type_parameters interface_decl_list END'''
    p[0] = program.Interface(p[2], p[3], p[4])

def p_service(p):
    '''top_level_decl : SERVICE UPPER_NAME OPEN_PARENS dependencies CLOSE_PARENS service_decl_list END'''
    p[0] = program.Service(p[2], p[4], p[6])

def p_entry(p):
    '''top_level_decl : ENTRY code_block END'''
    p[0] = program.Entry(p[2])

def p_type_parameters_empty(p):
    '''type_parameters : empty'''
    p[0] = []

def p_type_parameters(p):
    '''type_parameters : OPEN_PARENS non_empty_type_parameters CLOSE_PARENS'''
    p[0] = p[2]

def p_non_empty_type_parameters_initial(p):
    '''non_empty_type_parameters : LOWER_NAME'''
    p[0] = [p[1]]

def p_non_empty_type_parameters(p):
    '''non_empty_type_parameters : non_empty_type_parameters COMMA LOWER_NAME'''
    p[1].append(p[3])
    p[0] = p[1]

def p_enum_constructors_initial(p):
    '''enum_constructors : enum_constructor'''
    p[0] = [p[1]]

def p_enum_constructors(p):
    '''enum_constructors : enum_constructors PIPE enum_constructor'''
    p[1].append(p[3])
    p[0] = p[1]

def p_enum_constructor(p):
    '''enum_constructor : LOWER_NAME enum_type_list'''
    p[0] = program.EnumConstructor(p[1], p[2])

def p_empty_enum_type_list(p):
    '''enum_type_list : empty'''
    p[0] = []

def p_non_empty_enum_type_list(p):
    '''enum_type_list : OPEN_PARENS non_empty_enum_type_list CLOSE_PARENS'''
    p[0] = p[2]

def p_enum_type_list_initial(p):
    '''non_empty_enum_type_list : type'''
    p[0] = [p[1]]

def p_enum_type_list(p):
    '''non_empty_enum_type_list : non_empty_enum_type_list COMMA type'''
    p[1].append(p[3])
    p[0] = p[1]

def p_function(p):
    '''function : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS ARROW type DO code_block END'''
    p[0] = program.Function(p[2], p[4], p[7], p[9])

def p_coroutine(p):
    '''coroutine : COROUTINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS type ARROW type DO code_block END'''
    p[0] = program.Coroutine(p[2], p[4], p[6], p[8], p[10])

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
    '''dependency : LOWER_NAME COLON type'''
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
    '''record_decl : function'''
    p[0] = p[1]

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
    '''service_decl : IMPLEMENTS named_type optional_type_list service_method_list END'''
    p[0] = program.Implements(program_types.Instantiation(p[2], p[3]), p[4])

def p_optional_type_list_empty(p):
    '''optional_type_list : empty'''
    p[0] = []

def p_optional_type_list(p):
    '''optional_type_list : OPEN_PARENS non_empty_type_list CLOSE_PARENS'''
    p[0] = p[2]

def p_service_method_list_empty(p):
    '''service_method_list : empty'''
    p[0] = []

def p_service_method_list(p):
    '''service_method_list : service_method_list service_method'''
    p[1].append(p[2])
    p[0] = p[1]

def p_service_method(p):
    '''service_method : function'''
    p[0] = p[1]

def p_type_variable(p):
    '''type : LOWER_NAME'''
    p[0] = program_types.Variable(p[1])

def p_instantiation(p):
    '''type : named_type OPEN_PARENS non_empty_type_list CLOSE_PARENS'''
    p[0] = program_types.Instantiation(p[1], p[3])

def p_named_type(p):
    '''type : named_type'''
    p[0] = p[1]

def p_type_tuple(p):
    '''type : OPEN_PARENS type_list CLOSE_PARENS'''
    p[0] = program_types.Instantiation(program_types.tuple, p[2])

def p_type_named(p):
    '''named_type : UPPER_NAME'''
    p[0] = program_types.NamedType(None, p[1])

def p_type_named_qualified(p):
    '''named_type : LOWER_NAME DOT UPPER_NAME'''
    p[0] = program_types.NamedType(p[1], p[3])

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

def p_debug(p):
    '''statement : DEBUG OPEN_PARENS expression CLOSE_PARENS SEMICOLON'''
    p[0] = program.Debug(p[3])

def p_function_call_statement(p):
    '''statement : expression SEMICOLON'''
    p[0] = p[1]

def p_assignment_statement(p):
    '''statement : LOWER_NAME ASSIGNMENT expression SEMICOLON'''
    p[0] = program.Assignment(p[1], p[3])

def p_attr_assignment(p):
    '''statement : PROPERTY ASSIGNMENT expression SEMICOLON'''
    p[0] = program.AttrStore(p[1][1:], p[3])

def p_tuple_assignment(p):
    '''statement : non_empty_match_list COMMA LOWER_NAME ASSIGNMENT expression SEMICOLON'''
    p[1].append(p[3])
    p[0] = program.TupleDestructure(p[1], p[5])

def p_conditional(p):
    '''statement : IF OPEN_PARENS expression CLOSE_PARENS code_block if_end'''
    p[0] = program.Conditional(p[3], p[5], p[6])

def p_condition_end(p):
    '''if_end : END'''
    p[0] = program.CodeBlock([])

def p_else(p):
    '''if_end : ELSE code_block END'''
    p[0] = p[2]

def p_elif(p):
    '''if_end : ELSIF OPEN_PARENS expression CLOSE_PARENS code_block if_end'''
    p[0] = program.CodeBlock([program.Conditional(p[3], p[5], p[6])])

def p_for(p):
    '''statement : FOR LOWER_NAME IN expression DO code_block END'''
    p[0] = program.For(p[2], p[4], p[6])

def p_while(p):
    '''statement : DO code_block WHILE OPEN_PARENS expression CLOSE_PARENS'''
    p[0] = program.While(p[2], p[5])

def p_match(p):
    '''statement : MATCH OPEN_PARENS expression CLOSE_PARENS match_clauses END'''
    p[0] = program.Match(p[3], p[5])

def p_expression_variable(p):
    '''expression : LOWER_NAME'''
    p[0] = program.Variable(p[1])

def p_expression_type_name(p):
    '''expression : UPPER_NAME'''
    p[0] = program.TypeName(p[1])

def p_expression_char(p):
    '''expression : CHAR'''
    p[0] = program.CharLiteral(unicode(p[1]))

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

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = program.StringLiteral(p[1][1:-1])

def p_expression_sys_call(p):
    '''expression : SYS LOWER_NAME function_call'''
    p[0] = program.SysCall(p[2], p[3])

def p_expression_op_call(p):
    '''expression : OP STRING function_call'''
    p[0] = program.OpCall(p[2][1:-1], p[3])

def p_expression_attr(p):
    '''expression : PROPERTY'''
    p[0] = program.AttrLoad(p[1][1:])

def p_expression_yield(p):
    '''expression : YIELD expression'''
    p[0] = program.Yield(p[2])

def p_expression_run(p):
    '''expression : RUN OPEN_PARENS expression CLOSE_PARENS'''
    p[0] = program.Run(p[3])

def p_expression_resume(p):
    '''expression : RESUME OPEN_PARENS expression COMMA expression CLOSE_PARENS'''
    p[0] = program.Resume(p[3], p[5])

def p_expression_is_done(p):
    '''expression : IS_DONE OPEN_PARENS expression CLOSE_PARENS'''
    p[0] = program.IsDone(p[3])

def p_expression_tuple(p):
    '''expression : OPEN_PARENS non_empty_argument_list COMMA expression CLOSE_PARENS'''
    p[2].append(p[4])
    p[0] = program.TupleConstructor(p[2])

def p_expression_list(p):
    '''expression : OPEN_SQUARE argument_list CLOSE_SQUARE'''
    p[0] = program.ListConstructor(p[2])

def p_bracketed_expr(p):
    '''expression : OPEN_PARENS expression CLOSE_PARENS'''
    p[0] = p[2]

precedence = (
    ('nonassoc', 'COLON'),
    ('right', 'YIELD'),
    ('left', 'AND', 'OR'),
    ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIV'),
    ('right', 'DOT'),
    ('right', 'NOT'),
    ('nonassoc', 'OPEN_PARENS')
)

def p_annotation(p):
    '''expression : expression COLON OPEN_PARENS type CLOSE_PARENS'''
    p[0] = program.Annotated(p[1], p[4])

def p_expression_not(p):
    '''expression : NOT expression'''
    p[0] = program.Not(p[2])

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
                  | expression NE expression
                  | expression OR expression
                  | expression AND expression'''
    p[0] = program.BinOp(p[1], p[3], p[2])

def p_call(p):
    '''expression : expression function_call'''
    p[0] = program.Call(p[1], p[2])

def p_record_access(p):
    '''expression : expression DOT LOWER_NAME'''
    p[0] = program.RecordAccess(p[1], p[3])

def p_type_access(p):
    '''expression : expression DOT UPPER_NAME'''
    p[0] = program.TypeAccess(p[1], p[3])

def p_clauses_empty(p):
    '''match_clauses : empty'''
    p[0] = []

def p_clauses(p):
    '''match_clauses : match_clauses match_clause'''
    p[1].append(p[2])
    p[0] = p[1]

def p_clause(p):
    '''match_clause : LOWER_NAME match_list DO code_block END'''
    p[0] = program.Clause(p[1], p[2], p[4])

def p_match_list_empty(p):
    '''match_list : empty'''
    p[0] = []

def p_match_list(p):
    '''match_list : OPEN_PARENS non_empty_match_list CLOSE_PARENS'''
    p[0] = p[2]

def p_non_empty_match_list_initial(p):
    '''non_empty_match_list : LOWER_NAME'''
    p[0] = [p[1]]

def p_non_empty_match_list(p):
    '''non_empty_match_list : non_empty_match_list COMMA LOWER_NAME'''
    p[1].append(p[3])
    p[0] = p[1]

def p_empty_return(p):
    '''block_end : RETURN SEMICOLON'''
    p[0] = program.Return(program.VoidLiteral())

def p_return(p):
    '''block_end : RETURN expression SEMICOLON'''
    p[0] = program.Return(p[2])

def p_throw(p):
    '''block_end : THROW expression SEMICOLON'''
    p[0] = program.Throw(p[2])

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
