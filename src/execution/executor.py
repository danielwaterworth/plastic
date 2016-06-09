from rpython.rlib.rarithmetic import r_ulonglong
from rpython.rlib.rstruct.runpack import runpack

import bytecode
import data

class ActivationRecord(object):
    def __init__(self, function, arguments):
        self.function = function

        block_value_offsets = []
        n_values = 0
        for block in function.blocks:
            block_value_offsets.append(len(arguments) + n_values)
            n_values += len(block.instructions)

        self.values = arguments + ['' for i in xrange(n_values)]
        self.block_value_offsets = block_value_offsets
        self.next_value = len(arguments)
        self.current_block = function.blocks[0]
        self.pc = 0

    def resolve_arguments(self, arguments):
        return [self.values[arg] for arg in arguments]

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
        assert block < len(self.function.blocks)
        self.next_value = self.block_value_offsets[block]
        self.pc = 0
        self.current_block = self.function.blocks[block]

    def lookup_var(self, var):
        assert var < len(self.values)
        return self.values[var]

class Executor(object):
    def __init__(self, program):
        self.program = program
        self.memory = [r_ulonglong(0) for i in xrange(1024**2)]
        self.stack = [ActivationRecord(program.functions['main'], [])]

    def run(self):
        while True:
            instr = self.stack[-1].next_instruction()
            if instr:
                if isinstance(instr, bytecode.FunctionCall):
                    self.stack.append(ActivationRecord(self.program.functions[instr.function], []))
                elif isinstance(instr, bytecode.SysCall):
                    arguments = self.stack[-1].resolve_arguments(instr.arguments)
                    if instr.function == 'exit':
                        return None
                    elif instr.function == 'sub':
                        assert len(arguments) == 2
                        a, b = arguments
                        self.stack[-1].retire(data.sub(a, b))
                    elif instr.function == 'add':
                        assert len(arguments) == 2
                        a, b = arguments
                        self.stack[-1].retire(data.add(a, b))
                    elif instr.function == 'lt':
                        assert len(arguments) == 2
                        a, b = arguments
                        self.stack[-1].retire(data.lt(a, b))
                    elif instr.function == 'print_num':
                        assert len(arguments) == 1
                        a = arguments[0]
                        print runpack('>Q', a)
                        self.stack[-1].retire('')
                    else:
                        raise NotImplementedError('sys_call not implemented: %s' % instr.function)
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
                    self.stack[-1].goto(term.block_index)
                elif isinstance(term, bytecode.Conditional):
                    raise NotImplementedError()
                else:
                    raise NotImplementedError('missing terminator implementation')
