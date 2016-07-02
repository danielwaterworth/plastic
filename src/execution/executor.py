from rpython.rlib.jit import JitDriver
import bytecode
import data
import operators
import pdb

def activation_record(function, arguments):
    assert function.num_arguments == len(arguments)
    values = arguments + [data.Invalid() for i in xrange(function.n_values)]
    last_block_index = 0
    current_block_index = 0
    pc = 0
    return (values, function, last_block_index, current_block_index, pc)

class ActivationRecord(object):
    def __init__(self, record):
        self.values, self.function, self.last_block_index, self.current_block_index, self.pc = record

    @property
    def record(self):
        return (self.values, self.function, self.last_block_index, self.current_block_index, self.pc)

    def resolve_variable(self, var):
        value = self.values[var]
        assert not isinstance(value, data.Invalid)
        self.values[var] = data.Invalid()
        return value

    def resolve_variable_list(self, variables):
        return [self.resolve_variable(var) for var in variables]

    def retire(self, value):
        self.values[self.next_value] = value
        self.pc += 1

    def retire_multiple(self, values):
        assert len(values) >= 1
        self.retire(values[0])
        for value in values[1:]:
            instr = self.next_instruction()
            assert isinstance(instr, bytecode.Unpack)
            self.retire(value)

    def copy(self):
        value = self.next_value - 1
        assert value >= 0
        return self.values[value].copy()

    def next_instruction(self):
        if len(self.current_block.instructions) <= self.pc:
            return None
        else:
            return self.current_block.instructions[self.pc]

    def terminator(self):
        return self.current_block.terminator

    def goto(self, block):
        assert block < len(self.function.blocks)

        self.last_block_index = self.current_block_index
        self.current_block_index = block

        self.pc = 0

    @property
    def current_block(self):
        return self.function.blocks[self.current_block_index]

    @property
    def next_value(self):
        return (self.function.block_value_offsets[self.current_block_index] + self.pc)

class Coroutine(data.Data):
    def __init__(self):
        self.stack = []
        self.done = False
        self.var = data.Void()

    def print_backtrace(self):
        print ''
        print 'backtrace:'
        for frame in self.stack:
            frame1 = ActivationRecord(frame)
            print '  %s:%d' % (frame1.function.name, frame1.next_value)
        print ''

jitdriver = JitDriver(
                    greens=[
                        'current_block_index',
                        'last_block_index',
                        'pc',
                        'function',
                        'program',
                        'sys_caller',
                    ],
                    reds=[
                        'coroutine',
                        'coroutine_stack',
                        'memory',
                        'values',
                    ]
                )

def execute(sys_caller, program, arguments):
    coroutine_stack = []
    memory = [data.Void()] * 1024**2

    for function_name, function in program.functions.iteritems():
        block_value_offsets = []
        n_values = 0
        for block in function.blocks:
            block_value_offsets.append(function.num_arguments + n_values)
            n_values += len(block.instructions)

        function.n_values = n_values
        function.block_value_offsets = block_value_offsets

    coroutine = Coroutine()
    values, function, last_block_index, current_block_index, pc = activation_record(program.functions['$main'], arguments)
    while True:
        jitdriver.jit_merge_point(
                current_block_index=current_block_index,
                last_block_index=last_block_index,
                pc=pc,
                function=function,
                program=program,
                sys_caller=sys_caller,
                coroutine=coroutine,
                coroutine_stack=coroutine_stack,
                memory=memory,
                values=values,
            )
        current_frame = ActivationRecord((values, function, last_block_index, current_block_index, pc))
        instr = current_frame.next_instruction()
        if instr:
            if isinstance(instr, bytecode.Phi):
                current_frame.retire(current_frame.resolve_variable(instr.inputs[current_frame.last_block_index]))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Copy):
                current_frame.retire(current_frame.copy())
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Move):
                current_frame.retire(current_frame.resolve_variable(instr.variable))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Operation):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                if instr.operator == 'is_done':
                    assert len(arguments) == 1
                    c = arguments[0]
                    assert isinstance(c, Coroutine)
                    current_frame.retire(data.Bool(c.done))
                else:
                    current_frame.retire_multiple(operators.operation(instr.operator, arguments))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.SysCall):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                current_frame.retire_multiple(sys_caller.sys_call(instr.function, arguments))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.FunctionCall):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                coroutine.stack.append(current_frame.record)
                current_frame = ActivationRecord(activation_record(program.functions[instr.function], arguments))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.NewCoroutine):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                function = program.functions[instr.function]
                c = Coroutine()
                c.stack.append(activation_record(function, arguments))
                current_frame.retire(c)
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Debug):
                value = current_frame.resolve_variable(instr.value)
                print value.debug()
                current_frame.retire(data.Void())
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantBool):
                current_frame.retire(data.Bool(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantByte):
                current_frame.retire(data.Byte(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantChar):
                current_frame.retire(data.Char(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantByteString):
                current_frame.retire(data.ByteString(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantString):
                current_frame.retire(data.String(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantInt):
                current_frame.retire(data.Int(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantUInt):
                current_frame.retire(data.UInt(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.ConstantDouble):
                current_frame.retire(data.Double(instr.value))
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Void):
                current_frame.retire(data.Void())
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Load):
                address = current_frame.resolve_variable(instr.address)
                assert isinstance(address, data.UInt)
                dat = memory[address.n]
                current_frame.retire(dat)
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Store):
                address = current_frame.resolve_variable(instr.address)
                value = current_frame.resolve_variable(instr.variable)
                assert isinstance(address, data.UInt)
                memory[address.n] = value
                current_frame.retire(data.Void())
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Get):
                current_frame.retire(coroutine.var)
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Put):
                coroutine.var = current_frame.resolve_variable(instr.variable)
                current_frame.retire(data.Void())
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.RunCoroutine):
                c = current_frame.resolve_variable(instr.coroutine)
                assert isinstance(c, Coroutine)
                coroutine.stack.append(current_frame.record)
                coroutine_stack.append(coroutine)
                coroutine = c
                current_frame = ActivationRecord(coroutine.stack.pop())
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Yield):
                value = current_frame.resolve_variable(instr.value)
                if coroutine_stack:
                    coroutine.stack.append(current_frame.record)
                    coroutine = coroutine_stack.pop()
                    current_frame = ActivationRecord(coroutine.stack.pop())
                    current_frame.retire(value)
                else:
                    raise Exception('yielded from top level coroutine')
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(instr, bytecode.Resume):
                c = current_frame.resolve_variable(instr.coroutine)
                assert isinstance(c, Coroutine)
                value = current_frame.resolve_variable(instr.value)

                coroutine.stack.append(current_frame.record)
                coroutine_stack.append(coroutine)
                coroutine = c
                current_frame = ActivationRecord(coroutine.stack.pop())
                current_frame.retire(value)
                values, function, last_block_index, current_block_index, pc = current_frame.record
            else:
                raise NotImplementedError('missing instruction implementation')
        else:
            term = current_frame.terminator()
            if isinstance(term, bytecode.Return):
                values = current_frame.resolve_variable_list(term.variables)

                if coroutine.stack:
                    current_frame = ActivationRecord(coroutine.stack.pop())
                    current_frame.retire_multiple(values)
                else:
                    assert len(values) == 1
                    coroutine.done = True

                    if coroutine_stack:
                        coroutine = coroutine_stack.pop()
                        current_frame = ActivationRecord(coroutine.stack.pop())
                        current_frame.retire(values[0])
                    else:
                        return 0
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(term, bytecode.Goto):
                current_frame.goto(term.block_index)
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(term, bytecode.Conditional):
                v = current_frame.resolve_variable(term.condition_variable)
                assert isinstance(v, data.Bool)
                if v.b:
                    current_frame.goto(term.true_block)
                else:
                    current_frame.goto(term.false_block)
                values, function, last_block_index, current_block_index, pc = current_frame.record
            elif isinstance(term, bytecode.CatchFireAndDie):
                coroutine.print_backtrace()
                raise Exception('catching fire and dying')
            elif isinstance(term, bytecode.Throw):
                coroutine.print_backtrace()
                exception = current_frame.resolve_variable(term.exception)
                print exception
                raise Exception('throw')
            else:
                raise NotImplementedError('missing terminator implementation')
