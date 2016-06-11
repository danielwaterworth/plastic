class Function(object):
    def __init__(self, name, parameters, basic_blocks):
        self.name = name
        self.parameters = parameters
        self.basic_blocks = basic_blocks

class BasicBlock(object):
    def __init__(self, terminator, label=None, phi_nodes=[], statements=[]):
        self.label = label
        self.phi_nodes = phi_nodes
        self.statements = statements
        self.terminator = terminator

class Phi(object):
    def __init__(self, name, items):
        self.name = name
        self.items = items

class Statement(object):
    pass

class Assignment(Statement):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

class FunctionCallStatement(Statement):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class SysCallStatement(Statement):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class Store(Statement):
    def __init__(self, address, value):
        self.address = address
        self.value = value

class Expression(object):
    pass

class BinOp(Expression):
    def __init__(self, lhs, rhs, operator):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

class SysCallExpression(Expression):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class FunctionCallExpression(Expression):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class Load(Expression):
    def __init__(self, address):
        self.address = address

class NumberLiteral(Expression):
    def __init__(self, n):
        self.n = n

class Terminator(object):
    pass

class Return(Terminator):
    def __init__(self, variable):
        self.variable = variable

class Goto(Terminator):
    def __init__(self, block):
        self.block = block

class Condition(Terminator):
    def __init__(self, variable, true_block, false_block):
        self.variable = variable
        self.true_block = true_block
        self.false_block = false_block
