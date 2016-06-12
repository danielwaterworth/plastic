import ply.yacc as yacc

from lexer import tokens
import program

def p_program_empty(p):
    '''program : empty'''
    p[0] = []

def p_program(p):
    '''program : program function'''
    p[1].append(p[2])
    p[0] = p[1]

def p_function(p):
    '''function : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS code_block END'''
    p[0] = program.Function(p[2], p[4], p[6])

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
    p[0] = p[1]

def p_type(p):
    '''type : BOOL
            | UINT'''
    pass

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
    '''non_empty_argument_list : LOWER_NAME'''
    p[0] = [p[1]]

def p_non_empty_argument_list(p):
    '''non_empty_argument_list : non_empty_argument_list COMMA LOWER_NAME'''
    p[1].append(p[3])
    p[0] = p[1]

def p_function_call_statement(p):
    '''statement : LOWER_NAME function_call SEMICOLON'''
    p[0] = program.FunctionCallStatement(p[1], p[2])

def p_assignment_statement(p):
    '''statement : LOWER_NAME ASSIGNMENT expression SEMICOLON'''
    p[0] = program.Assignment(p[1], p[3])

def p_statement_sys_call(p):
    '''statement : SYS LOWER_NAME function_call SEMICOLON'''
    p[0] = program.SysCallStatement(p[2], p[3])

def p_statement_store(p):
    '''statement : STORE LOWER_NAME LOWER_NAME SEMICOLON'''
    p[0] = program.Store(p[2], p[3])

def p_conditional(p):
    '''statement : IF OPEN_PARENS LOWER_NAME CLOSE_PARENS code_block ELSE code_block END'''
    p[0] = program.Conditional(p[3], p[5], p[7])

def p_while(p):
    '''statement : DO code_block WHILE OPEN_PARENS LOWER_NAME CLOSE_PARENS'''
    p[0] = program.While(p[2], p[5])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = program.NumberLiteral(int(p[1]))

def p_expression_true(p):
    '''expression : TRUE'''
    p[0] = program.BoolLiteral(True)

def p_expression_false(p):
    '''expression : FALSE'''
    p[0] = program.BoolLiteral(False)

def p_expression_sys_call(p):
    '''expression : SYS LOWER_NAME function_call'''
    p[0] = program.SysCallExpression(p[2], p[3])

def p_expression_call(p):
    '''expression : LOWER_NAME function_call'''
    p[0] = program.FunctionCallExpression(p[1], p[2])

def p_expression_load(p):
    '''expression : LOAD LOWER_NAME'''
    p[0] = program.Load(p[2])

def p_expression_binop(p):
    '''expression : LOWER_NAME PLUS LOWER_NAME
                  | LOWER_NAME MINUS LOWER_NAME
                  | LOWER_NAME MUL LOWER_NAME
                  | LOWER_NAME DIV LOWER_NAME
                  | LOWER_NAME LT LOWER_NAME
                  | LOWER_NAME LE LOWER_NAME
                  | LOWER_NAME GT LOWER_NAME
                  | LOWER_NAME GE LOWER_NAME
                  | LOWER_NAME EQ LOWER_NAME
                  | LOWER_NAME NE LOWER_NAME'''
    p[0] = program.BinOp(p[1], p[3], p[2])

def p_return(p):
    '''block_end : RETURN LOWER_NAME SEMICOLON'''
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
