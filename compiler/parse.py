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
    '''function : DEFINE LOWER_NAME OPEN_PARENS parameter_list CLOSE_PARENS function_body END'''
    p[0] = program.Function(p[2], p[4], p[6])

def p_parameter_list_empty(p):
    '''parameter_list : empty'''
    p[0] = []

def p_parameter_list(p):
    '''parameter_list : non_empty_parameter_list'''
    p[0] = p[1]

def p_non_empty_parameter_list_initial(p):
    '''non_empty_parameter_list : LOWER_NAME'''
    p[0] = p[1]

def p_non_empty_parameter_list(p):
    '''non_empty_parameter_list : non_empty_parameter_list COMMA LOWER_NAME'''
    p[1].append(p[3])
    p[0] = p[1]

def p_function_body_initial(p):
    '''function_body : basic_block'''
    p[0] = [p[1]]

def p_function_body(p):
    '''function_body : function_body basic_block'''
    p[1].append(p[2])
    p[0] = p[1]

def p_labelled_basic_block(p):
    '''basic_block : LOWER_NAME COLON phi_and_statement_list terminator SEMICOLON'''
    p[0] = program.BasicBlock(label=p[1], phi_nodes=p[3][0], statements=p[3][1], terminator=p[4])

def p_basic_block_phis(p):
    '''basic_block : LOWER_NAME ASSIGNMENT phi_expression SEMICOLON phi_and_statement_list terminator SEMICOLON'''
    phi = program.Phi(p[1], p[3])
    p[0] = program.BasicBlock(phi_nodes=[phi] + p[5][0], statements=p[5][1], terminator=p[6])

def p_basic_block_assignment(p):
    '''basic_block : LOWER_NAME ASSIGNMENT expression SEMICOLON statement_list terminator SEMICOLON'''
    statement = program.Assignment(p[1], p[3])
    p[0] = program.BasicBlock(statements=[statement] + p[5], terminator=p[6])

def p_basic_block_function_call(p):
    '''basic_block : LOWER_NAME function_call SEMICOLON statement_list terminator SEMICOLON'''
    statement = program.FunctionCallStatement(p[1], p[2])
    p[0] = program.BasicBlock(statements=[statement] + p[4], terminator=p[5])

def p_basic_block_statement_without_lowen_name(p):
    '''basic_block : statement_without_lower_name SEMICOLON statement_list terminator SEMICOLON'''
    p[0] = program.BasicBlock(statements=[p[1]] + p[3], terminator=p[4])

def p_basic_block_terminator(p):
    '''basic_block : terminator SEMICOLON'''
    p[0] = program.BasicBlock(terminator=p[1])

def p_phi_and_statement_list_1(p):
    '''phi_and_statement_list : LOWER_NAME ASSIGNMENT phi_expression SEMICOLON phi_and_statement_list'''
    phi = program.Phi(p[1], p[3])
    p[0] = ([phi] + p[5][0], p[5][1])

def p_phi_and_statement_list_2(p):
    '''phi_and_statement_list : LOWER_NAME ASSIGNMENT expression SEMICOLON statement_list'''
    statement = program.Assignment(p[1], p[3])
    p[0] = ([], [statement] + p[5])

def p_phi_and_statement_list_3(p):
    '''phi_and_statement_list : LOWER_NAME function_call SEMICOLON statement_list'''
    statement = program.FunctionCallStatement(p[1], p[2])
    p[0] = ([], [statement] + p[4])

def p_phi_and_statement_list_4(p):
    '''phi_and_statement_list : statement_without_lower_name SEMICOLON statement_list'''
    p[0] = ([], [p[1]] + p[3])

def p_phi_and_statement_list_empty(p):
    '''phi_and_statement_list : empty'''
    p[0] = ([], [])

def p_phi_expression(p):
    '''phi_expression : PHI phi_list'''
    p[0] = p[2]

def p_phi_list_initial(p):
    '''phi_list : phi_item'''
    p[0] = [p[1]]

def p_phi_list(p):
    '''phi_list : phi_list COMMA phi_item'''
    p[1].append(p[3])
    p[0] = p[1]

def p_phi_item(p):
    '''phi_item : OPEN_PARENS LOWER_NAME COMMA LOWER_NAME CLOSE_PARENS'''
    p[0] = (p[2], p[4])

def p_statement_list_empty(p):
    '''statement_list : empty'''
    p[0] = []

def p_statement_list(p):
    '''statement_list : statement_list statement SEMICOLON'''
    p[1].append(p[2])
    p[0] = p[1]

def p_function_call_call(p):
    '''function_call : OPEN_PARENS argument_list CLOSE_PARENS'''
    p[0] = p[2]

def p_function_call_statement(p):
    '''statement : LOWER_NAME function_call'''
    p[0] = program.FunctionCallStatement(p[1], p[2])

def p_assignment_statement(p):
    '''statement : LOWER_NAME ASSIGNMENT expression'''
    p[0] = program.Assignment(p[1], p[3])

def p_statement(p):
    '''statement : statement_without_lower_name'''
    p[0] = p[1]

def p_statement_sys_call(p):
    '''statement_without_lower_name : SYS LOWER_NAME function_call'''
    p[0] = program.SysCallStatement(p[2], p[3])

def p_statement_store(p):
    '''statement_without_lower_name : STORE LOWER_NAME LOWER_NAME'''
    p[0] = program.Store(p[2], p[3])

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

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = program.NumberLiteral(int(p[1]))

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
    '''terminator : RETURN LOWER_NAME'''
    p[0] = program.Return(p[2])

def p_goto(p):
    '''terminator : GOTO LOWER_NAME'''
    p[0] = program.Goto(p[2])

def p_condition(p):
    '''terminator : CONDITION LOWER_NAME LOWER_NAME LOWER_NAME'''
    p[0] = program.Condition(p[2], p[3], p[4])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    raise Exception("Syntax error in input!")

parser = yacc.yacc()
