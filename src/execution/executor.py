from rpython.rlib.rarithmetic import r_ulonglong
from rpython.rlib.rstruct.runpack import runpack

import bytecode
import data

class ActivationRecord(object):
    def __init__(self, function, arguments):
        assert function.num_arguments == len(arguments)
        self.function = function

        block_value_offsets = []
        n_values = 0
        for block in function.blocks:
            block_value_offsets.append(len(arguments) + n_values)
            n_values += len(block.instructions)

        self.values = arguments + ['' for i in xrange(n_values)]
        self.block_value_offsets = block_value_offsets
        self.next_value = len(arguments)
        self.last_block_index = 0
        self.current_block_index = 0
        self.current_block = function.blocks[0]
        self.pc = 0

    def resolve_variable(self, var):
        return self.values[var]

    def resolve_variable_list(self, variables):
        return [self.resolve_variable(var) for var in variables]

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

        self.last_block_index = self.current_block_index
        self.current_block_index = block

        self.next_value = self.block_value_offsets[block]
        self.pc = 0
        self.current_block = self.function.blocks[block]

    def lookup_var(self, var):
        assert var < len(self.values)
        return self.values[var]

class CoroutineExit(object):
    pass

class CoroutineReturn(CoroutineExit):
    def __init__(self, value):
        self.value = value

class CoroutineYield(CoroutineExit):
    def __init__(self, value):
        self.value = value

class CoroutineNew(CoroutineExit):
    def __init__(self, function, arguments):
        self.function = function
        self.arguments = arguments

class CoroutineRun(CoroutineExit):
    def __init__(self, coroutine_id):
        self.coroutine_id = coroutine_id

class CoroutineResume(CoroutineExit):
    def __init__(self, coroutine_id, value):
        self.coroutine_id = coroutine_id
        self.value = value

class Coroutine(object):
    def __init__(self, executor, program, function, arguments):
        self.executor = executor
        self.program = program
        self.stack = [ActivationRecord(function, arguments)]

    def run(self):
        while True:
            instr = self.stack[-1].next_instruction()
            if instr:
                if isinstance(instr, bytecode.Phi):
                    self.stack[-1].retire(self.stack[-1].resolve_variable(instr.inputs[self.stack[-1].last_block_index]))
                elif isinstance(instr, bytecode.Operation):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    self.stack[-1].retire(data.operation(instr.operator, arguments))
                elif isinstance(instr, bytecode.SysCall):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    if instr.function == 'exit':
                        return None
                    elif instr.function == 'print_num':
                        assert len(arguments) == 1
                        a = arguments[0]
                        assert len(a) == 8
                        print runpack('>Q', a)
                        self.stack[-1].retire('')
                    elif instr.function == 'print_bool':
                        assert len(arguments) == 1
                        a = arguments[0]
                        assert len(a) == 1
                        if a != '\0':
                            print 'True'
                        else:
                            print 'False'
                        self.stack[-1].retire('')
                    elif instr.function == 'print_byte':
                        assert len(arguments) == 1
                        a = arguments[0]
                        assert len(a) == 1
                        print a
                        self.stack[-1].retire('')
                    else:
                        raise NotImplementedError('sys_call not implemented: %s' % instr.function)
                elif isinstance(instr, bytecode.FunctionCall):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    self.stack.append(ActivationRecord(self.program.functions[instr.function], arguments))
                elif isinstance(instr, bytecode.NewCoroutine):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    return CoroutineNew(instr.function, arguments)
                elif isinstance(instr, bytecode.Constant):
                    self.stack[-1].retire(instr.value)
                elif isinstance(instr, bytecode.Load):
                    address_bytes = self.stack[-1].resolve_variable(instr.address)
                    assert len(address_bytes) == 8
                    address = runpack('>Q', address_bytes)
                    dat = self.executor.memory[address]
                    self.stack[-1].retire(dat)
                elif isinstance(instr, bytecode.Store):
                    address_bytes = self.stack[-1].resolve_variable(instr.address)
                    value = self.stack[-1].resolve_variable(instr.variable)
                    assert len(address_bytes) == 8
                    address = runpack('>Q', address_bytes)
                    self.executor.memory[address] = value
                    self.stack[-1].retire('')
                elif isinstance(instr, bytecode.RunCoroutine):
                    coroutine = self.stack[-1].resolve_variable(instr.coroutine)
                    return CoroutineRun(coroutine)
                elif isinstance(instr, bytecode.Yield):
                    value = self.stack[-1].resolve_variable(instr.value)
                    return CoroutineYield(value)
                elif isinstance(instr, bytecode.Resume):
                    coroutine = self.stack[-1].resolve_variable(instr.coroutine)
                    value = self.stack[-1].resolve_variable(instr.value)
                    return CoroutineResume(coroutine, value)
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
                        return CoroutineReturn(value)
                elif isinstance(term, bytecode.Goto):
                    self.stack[-1].goto(term.block_index)
                elif isinstance(term, bytecode.Conditional):
                    v = self.stack[-1].resolve_variable(term.condition_variable)
                    assert len(v) == 1
                    if v != chr(0):
                        self.stack[-1].goto(term.true_block)
                    else:
                        self.stack[-1].goto(term.false_block)
                elif isinstance(term, bytecode.CatchFireAndDie):
                    raise Exception('catching fire and dying')
                else:
                    raise NotImplementedError('missing terminator implementation')

    def resume(self, value):
        self.stack[-1].retire(value)
        return self.run()

class Executor(object):
    def __init__(self, program):
        self.program = program
        self.coroutines = []
        self.coroutine_stack = [Coroutine(self, program, program.functions['$main'], [])]
        self.memory = [''] * 1024**2

    def run(self):
        coroutine = self.coroutine_stack[-1]
        result = coroutine.run()
        while True:
            if isinstance(result, CoroutineReturn):
                self.coroutine_stack.pop()
                if self.coroutine_stack:
                    coroutine = self.coroutine_stack[-1]
                    result = coroutine.resume(result.value)
                else:
                    return 0
            elif isinstance(result, CoroutineYield):
                self.coroutine_stack.pop()
                if self.coroutine_stack:
                    coroutine = self.coroutine_stack[-1]
                    result = coroutine.resume(result.value)
                else:
                    raise Exception('yielded from top level coroutine')
            elif isinstance(result, CoroutineResume):
                coroutine = self.coroutines[runpack('>Q', result.coroutine_id)]
                self.coroutine_stack.append(coroutine)
                result = coroutine.resume(result.value)
            elif isinstance(result, CoroutineNew):
                function = self.program.functions[result.function]
                coroutine = Coroutine(self, self.program, function, result.arguments)
                coroutine_id = data.pack_uint(len(self.coroutines))
                self.coroutines.append(coroutine)
                result = self.coroutine_stack[-1].resume(coroutine_id)
            elif isinstance(result, CoroutineRun):
                coroutine = self.coroutines[runpack('>Q', result.coroutine_id)]
                self.coroutine_stack.append(coroutine)
                result = coroutine.run()
