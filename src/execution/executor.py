import bytecode
import data
import operators

class ActivationRecord(object):
    def __init__(self, function, arguments):
        assert function.num_arguments == len(arguments)
        self.function = function

        block_value_offsets = []
        n_values = 0
        for block in function.blocks:
            block_value_offsets.append(len(arguments) + n_values)
            n_values += len(block.instructions)

        self.values = arguments + [data.Void() for i in xrange(n_values)]
        self.block_value_offsets = block_value_offsets
        self.next_value = len(arguments)
        self.last_block_index = 0
        self.current_block_index = 0
        self.current_block = function.blocks[0]
        self.pc = 0

    def resolve_variable(self, var):
        value = self.values[var]
        assert not isinstance(value, data.Invalid)
        self.values[var] = data.Invalid()
        return value

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

    def copy(self):
        assert self.next_value > 1
        return self.values[self.next_value-1].copy()

    def goto(self, block):
        assert block < len(self.function.blocks)

        self.last_block_index = self.current_block_index
        self.current_block_index = block

        self.next_value = self.block_value_offsets[block]
        self.pc = 0
        self.current_block = self.function.blocks[block]

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
    def __init__(self, coroutine):
        assert isinstance(coroutine, Coroutine)
        self.coroutine = coroutine

class CoroutineResume(CoroutineExit):
    def __init__(self, coroutine, value):
        assert isinstance(coroutine, Coroutine)
        self.coroutine = coroutine
        self.value = value

class Coroutine(data.Data):
    def __init__(self, executor, program, function, arguments):
        self.executor = executor
        self.program = program
        self.stack = [ActivationRecord(function, arguments)]
        self.done = False
        self.var = data.Void()

    def run(self):
        assert not self.done
        while True:
            instr = self.stack[-1].next_instruction()
            if instr:
                if isinstance(instr, bytecode.Phi):
                    self.retire(self.stack[-1].resolve_variable(instr.inputs[self.stack[-1].last_block_index]))
                elif isinstance(instr, bytecode.Copy):
                    self.retire(self.stack[-1].copy())
                elif isinstance(instr, bytecode.Move):
                    self.retire(self.stack[-1].resolve_variable(instr.variable))
                elif isinstance(instr, bytecode.Operation):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    if instr.operator == 'is_done':
                        assert len(arguments) == 1
                        coroutine = arguments[0]
                        assert isinstance(coroutine, Coroutine)
                        self.retire(data.Bool(coroutine.done))
                    else:
                        self.retire_multiple(operators.operation(instr.operator, arguments))
                elif isinstance(instr, bytecode.SysCall):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    self.retire_multiple(self.executor.sys_caller.sys_call(instr.function, arguments))
                elif isinstance(instr, bytecode.FunctionCall):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    self.stack.append(ActivationRecord(self.program.functions[instr.function], arguments))
                elif isinstance(instr, bytecode.NewCoroutine):
                    arguments = self.stack[-1].resolve_variable_list(instr.arguments)
                    return CoroutineNew(instr.function, arguments)
                elif isinstance(instr, bytecode.Debug):
                    value = self.stack[-1].resolve_variable(instr.value)
                    print value.debug()
                    self.retire(data.Void())
                elif isinstance(instr, bytecode.ConstantBool):
                    self.retire(data.Bool(instr.value))
                elif isinstance(instr, bytecode.ConstantByte):
                    self.retire(data.Byte(instr.value))
                elif isinstance(instr, bytecode.ConstantChar):
                    self.retire(data.Char(instr.value))
                elif isinstance(instr, bytecode.ConstantByteString):
                    self.retire(data.ByteString(instr.value))
                elif isinstance(instr, bytecode.ConstantString):
                    self.retire(data.String(instr.value))
                elif isinstance(instr, bytecode.ConstantInt):
                    self.retire(data.Int(instr.value))
                elif isinstance(instr, bytecode.ConstantUInt):
                    self.retire(data.UInt(instr.value))
                elif isinstance(instr, bytecode.ConstantDouble):
                    self.retire(data.Double(instr.value))
                elif isinstance(instr, bytecode.Void):
                    self.retire(data.Void())
                elif isinstance(instr, bytecode.Load):
                    address = self.stack[-1].resolve_variable(instr.address)
                    assert isinstance(address, data.UInt)
                    dat = self.executor.memory[address.n]
                    self.retire(dat)
                elif isinstance(instr, bytecode.Store):
                    address = self.stack[-1].resolve_variable(instr.address)
                    value = self.stack[-1].resolve_variable(instr.variable)
                    assert isinstance(address, data.UInt)
                    self.executor.memory[address.n] = value
                    self.retire(data.Void())
                elif isinstance(instr, bytecode.Get):
                    self.retire(self.var)
                elif isinstance(instr, bytecode.Put):
                    self.var = self.stack[-1].resolve_variable(instr.variable)
                    self.retire(data.Void())
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
                    frame = self.stack.pop()
                    values = frame.resolve_variable_list(term.variables)
                    if self.stack:
                        self.retire_multiple(values)
                    else:
                        assert len(values) == 1
                        self.done = True
                        return CoroutineReturn(values[0])
                elif isinstance(term, bytecode.Goto):
                    self.stack[-1].goto(term.block_index)
                elif isinstance(term, bytecode.Conditional):
                    v = self.stack[-1].resolve_variable(term.condition_variable)
                    assert isinstance(v, data.Bool)
                    if v.b:
                        self.stack[-1].goto(term.true_block)
                    else:
                        self.stack[-1].goto(term.false_block)
                elif isinstance(term, bytecode.CatchFireAndDie):
                    raise Exception('catching fire and dying')
                elif isinstance(term, bytecode.Throw):
                    exception = self.stack[-1].resolve_variable(term.exception)
                    print exception
                    raise Exception('throw')
                else:
                    raise NotImplementedError('missing terminator implementation')

    def retire(self, value):
        self.stack[-1].retire(value)

    def retire_multiple(self, values):
        assert len(values) >= 1
        self.retire(values[0])
        for value in values[1:]:
            instr = self.stack[-1].next_instruction()
            assert isinstance(instr, bytecode.Unpack)
            self.retire(value)

    def resume(self, value):
        assert len(self.stack) > 0
        self.retire(value)
        return self.run()

class Executor(object):
    def __init__(self, sys_caller, program):
        self.sys_caller = sys_caller
        self.program = program
        self.coroutine_stack = [Coroutine(self, program, program.functions['$main'], [])]
        self.memory = [data.Void()] * 1024**2

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
                self.coroutine_stack.append(result.coroutine)
                result = result.coroutine.resume(result.value)
            elif isinstance(result, CoroutineNew):
                function = self.program.functions[result.function]
                coroutine = Coroutine(self, self.program, function, result.arguments)
                result = self.coroutine_stack[-1].resume(coroutine)
            elif isinstance(result, CoroutineRun):
                self.coroutine_stack.append(result.coroutine)
                result = coroutine.run()
