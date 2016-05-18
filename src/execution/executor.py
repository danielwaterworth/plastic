from rpython.rlib.rarithmetic import r_ulonglong

import bytecode
import data

class ActivationRecord(object):
    def __init__(self, function):
        self.function = function

        n_values = 0
        for block in function.blocks:
            n_values += len(block.instructions)

        self.values = ['' for i in xrange(n_values)]
        self.next_value = 0
        self.current_block = function.blocks[0]
        self.pc = 0

    def next_instruction(self):
        if len(self.current_block.instructions) <= self.pc:
            return None
        else:
            return self.current_block.instructions[self.pc]

    def terminator(self):
        return self.current_block.terminator

    def retire(self, value):
        self.values[self.next_value] = value
        self.next_value += 1
        self.pc += 1

    def goto(self, block):
        pass

    def lookup_var(self, var):
        assert var < len(self.values)
        return self.values[var]

class Executor(object):
    def __init__(self, program):
        self.program = program
        self.memory = [r_ulonglong(0) for i in xrange(1024**2)]
        self.stack = [ActivationRecord(program.functions['main'])]

    def run(self):
        while True:
            instr = self.stack[-1].next_instruction()
            if instr:
                if isinstance(instr, bytecode.FunctionCall):
                    raise NotImplementedError()
                elif isinstance(instr, bytecode.SysCall):
                    if instr.function == 'hello_world':
                        print 'Hello, world!'
                        self.stack[-1].retire('')
                    elif instr.function == 'exit':
                        return None
                    else:
                        raise NotImplementedError()
                elif isinstance(instr, bytecode.Constant):
                    self.stack[-1].retire(instr.value)
                else:
                    raise NotImplementedError('missing instruction implementation')
            else:
                term = self.stack[-1].terminator()
                if isinstance(term, bytecode.Return):
                    value = self.stack[-1].lookup_var(term.variable)
                    self.stack.pop()
                    if self.stack:
                        self.stack[-1].retire(value)
                    else:
                        return value
                elif isinstance(term, bytecode.Goto):
                    raise NotImplementedError()
                elif isinstance(term, bytecode.Conditional):
                    raise NotImplementedError()
                else:
                    raise NotImplementedError('missing terminator implementation')
