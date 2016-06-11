import ply.yacc as yacc

from lexer import tokens

def p_program_empty(p):
    '''program : empty'''
    return []

def p_program(p):
    '''program : program function'''
    pass

def p_function(p):
    '''function : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS function_body END'''
    pass

def p_parameter_list_empty(p):
    '''parameter_list : empty'''
    pass

def p_parameter_list(p):
    '''parameter_list : non_empty_parameter_list'''
    pass

def p_non_empty_parameter_list_initial(p):
    '''non_empty_parameter_list : LOWER_NAME'''
    pass

def p_non_empty_parameter_list(p):
    '''non_empty_parameter_list : non_empty_parameter_list COMMA LOWER_NAME'''
    pass

def p_function_body_initial(p):
    '''function_body : basic_block
                     | function_body basic_block'''
    pass

def p_basic_block(p):
    '''basic_block : LOWER_NAME COLON phi_and_statement_list terminator SEMICOLON
                   | LOWER_NAME ASSIGNMENT phi_expression SEMICOLON phi_and_statement_list terminator SEMICOLON
                   | LOWER_NAME ASSIGNMENT expression SEMICOLON statement_list terminator SEMICOLON
                   | LOWER_NAME statement_ending SEMICOLON statement_list terminator SEMICOLON
                   | statement_without_lower_name SEMICOLON statement_list terminator SEMICOLON
                   | terminator SEMICOLON'''
    pass

def p_phi_expression(p):
    '''phi_expression : PHI phi_list'''
    pass

def p_phi_list_initial(p):
    '''phi_list : phi_item'''
    pass

def p_phi_list(p):
    '''phi_list : phi_list COMMA phi_item'''
    pass

def p_phi_item(p):
    '''phi_item : OPEN_PARENS LOWER_NAME COMMA LOWER_NAME CLOSE_PARENS'''
    pass

def p_phi_and_statement_list(p):
    '''phi_and_statement_list : LOWER_NAME ASSIGNMENT phi_expression SEMICOLON phi_and_statement_list
                              | LOWER_NAME ASSIGNMENT expression SEMICOLON statement_list
                              | LOWER_NAME statement_ending SEMICOLON statement_list
                              | statement_without_lower_name SEMICOLON statement_list
                              | empty'''
    pass

def p_statement_list_empty(p):
    '''statement_list : empty'''
    pass

def p_statement_list(p):
    '''statement_list : statement_list statement SEMICOLON'''
    pass

def p_statement_ending_call(p):
    '''statement_ending : OPEN_PARENS argument_list CLOSE_PARENS'''
    pass

def p_statement(p):
    '''statement : LOWER_NAME statement_ending
                 | LOWER_NAME ASSIGNMENT expression
                 | statement_without_lower_name'''
    pass

def p_statement_sys_call(p):
    '''statement_without_lower_name : SYS LOWER_NAME OPEN_PARENS argument_list CLOSE_PARENS'''
    pass

def p_statement_store(p):
    '''statement_without_lower_name : STORE LOWER_NAME LOWER_NAME'''
    pass

def p_argument_list_empty(p):
    '''argument_list : empty'''
    pass

def p_argument_list(p):
    '''argument_list : non_empty_argument_list'''
    pass

def p_non_empty_argument_list_initial(p):
    '''non_empty_argument_list : LOWER_NAME'''
    pass

def p_non_empty_argument_list(p):
    '''non_empty_argument_list : non_empty_argument_list COMMA LOWER_NAME'''
    pass

def p_expression_number(p):
    '''expression : NUMBER'''
    pass

def p_expression_sys_call(p):
    '''expression : SYS LOWER_NAME OPEN_PARENS argument_list CLOSE_PARENS'''
    pass

def p_expression_call(p):
    '''expression : LOWER_NAME OPEN_PARENS argument_list CLOSE_PARENS'''
    pass

def p_expression_load(p):
    '''expression : LOAD LOWER_NAME'''
    pass

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
    pass

def p_return(p):
    '''terminator : RETURN LOWER_NAME'''
    pass

def p_goto(p):
    '''terminator : GOTO LOWER_NAME'''

def p_condition(p):
    '''terminator : CONDITION LOWER_NAME LOWER_NAME LOWER_NAME'''

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    raise Exception("Syntax error in input!")

parser = yacc.yacc()
