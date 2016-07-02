from rpython.rlib.jit import JitDriver
import bytecode
import data
import operators
import pdb

class ActivationRecord(object):
    def __init__(self, function, arguments):
        assert function.num_arguments == len(arguments)
        self.function = function
        self.values = arguments + [data.Invalid() for i in xrange(function.n_values)]
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

    def goto(self, block):
        assert block < len(self.function.blocks)

        self.last_block_index = self.current_block_index
        self.current_block_index = block

        self.pc = 0
        self.current_block = self.function.blocks[block]

    @property
    def next_value(self):
        return (self.function.block_value_offsets[self.current_block_index] + self.pc)

class Coroutine(data.Data):
    def __init__(self, function, arguments):
        self.stack = []
        self.current_frame = ActivationRecord(function, arguments)
        self.done = False
        self.var = data.Void()

    def print_backtrace(self):
        print ''
        print 'backtrace:'
        for frame in self.stack:
            print '  %s:%d' % (frame.function.name, frame.next_value)
        print ''

jitdriver = JitDriver(greens=['sys_caller', 'program'], reds=['coroutine_stack', 'current_frame', 'coroutine', 'memory'])

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

    coroutine = Coroutine(program.functions['$main'], arguments)
    current_frame = coroutine.current_frame
    while True:
        jitdriver.jit_merge_point(
                coroutine_stack=coroutine_stack,
                memory=memory,
                current_frame=current_frame,
                coroutine=coroutine,
                sys_caller=sys_caller,
                program=program
            )
        instr = current_frame.next_instruction()
        if instr:
            if isinstance(instr, bytecode.Phi):
                current_frame.retire(current_frame.resolve_variable(instr.inputs[current_frame.last_block_index]))
            elif isinstance(instr, bytecode.Copy):
                current_frame.retire(current_frame.copy())
            elif isinstance(instr, bytecode.Move):
                current_frame.retire(current_frame.resolve_variable(instr.variable))
            elif isinstance(instr, bytecode.Operation):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                if instr.operator == 'is_done':
                    assert len(arguments) == 1
                    c = arguments[0]
                    assert isinstance(c, Coroutine)
                    current_frame.retire(data.Bool(c.done))
                else:
                    current_frame.retire_multiple(operators.operation(instr.operator, arguments))
            elif isinstance(instr, bytecode.SysCall):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                current_frame.retire_multiple(sys_caller.sys_call(instr.function, arguments))
            elif isinstance(instr, bytecode.FunctionCall):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                coroutine.stack.append(current_frame)
                current_frame = ActivationRecord(program.functions[instr.function], arguments)
                coroutine.current_frame = current_frame
            elif isinstance(instr, bytecode.NewCoroutine):
                arguments = current_frame.resolve_variable_list(instr.arguments)
                function = program.functions[instr.function]
                c = Coroutine(function, arguments)
                current_frame.retire(c)
            elif isinstance(instr, bytecode.Debug):
                value = current_frame.resolve_variable(instr.value)
                print value.debug()
                current_frame.retire(data.Void())
            elif isinstance(instr, bytecode.ConstantBool):
                current_frame.retire(data.Bool(instr.value))
            elif isinstance(instr, bytecode.ConstantByte):
                current_frame.retire(data.Byte(instr.value))
            elif isinstance(instr, bytecode.ConstantChar):
                current_frame.retire(data.Char(instr.value))
            elif isinstance(instr, bytecode.ConstantByteString):
                current_frame.retire(data.ByteString(instr.value))
            elif isinstance(instr, bytecode.ConstantString):
                current_frame.retire(data.String(instr.value))
            elif isinstance(instr, bytecode.ConstantInt):
                current_frame.retire(data.Int(instr.value))
            elif isinstance(instr, bytecode.ConstantUInt):
                current_frame.retire(data.UInt(instr.value))
            elif isinstance(instr, bytecode.ConstantDouble):
                current_frame.retire(data.Double(instr.value))
            elif isinstance(instr, bytecode.Void):
                current_frame.retire(data.Void())
            elif isinstance(instr, bytecode.Load):
                address = current_frame.resolve_variable(instr.address)
                assert isinstance(address, data.UInt)
                dat = memory[address.n]
                current_frame.retire(dat)
            elif isinstance(instr, bytecode.Store):
                address = current_frame.resolve_variable(instr.address)
                value = current_frame.resolve_variable(instr.variable)
                assert isinstance(address, data.UInt)
                memory[address.n] = value
                current_frame.retire(data.Void())
            elif isinstance(instr, bytecode.Get):
                current_frame.retire(coroutine.var)
            elif isinstance(instr, bytecode.Put):
                coroutine.var = current_frame.resolve_variable(instr.variable)
                current_frame.retire(data.Void())
            elif isinstance(instr, bytecode.RunCoroutine):
                c = current_frame.resolve_variable(instr.coroutine)
                assert isinstance(c, Coroutine)
                coroutine_stack.append(coroutine)
                coroutine = c
                current_frame = coroutine.current_frame
            elif isinstance(instr, bytecode.Yield):
                value = current_frame.resolve_variable(instr.value)
                if coroutine_stack:
                    coroutine = coroutine_stack.pop()
                    current_frame = coroutine.current_frame
                    current_frame.retire(value)
                else:
                    raise Exception('yielded from top level coroutine')
            elif isinstance(instr, bytecode.Resume):
                c = current_frame.resolve_variable(instr.coroutine)
                assert isinstance(c, Coroutine)
                value = current_frame.resolve_variable(instr.value)

                coroutine_stack.append(coroutine)
                coroutine = c
                current_frame = coroutine.current_frame
                current_frame.retire(value)
            else:
                raise NotImplementedError('missing instruction implementation')
        else:
            term = current_frame.terminator()
            if isinstance(term, bytecode.Return):
                frame = current_frame

                try:
                    coroutine.current_frame = coroutine.stack.pop()
                except IndexError:
                    coroutine.current_frame = None
                current_frame = coroutine.current_frame

                values = frame.resolve_variable_list(term.variables)
                if current_frame:
                    current_frame.retire_multiple(values)
                else:
                    assert len(values) == 1
                    coroutine.done = True

                    if coroutine_stack:
                        coroutine = coroutine_stack.pop()
                        current_frame = coroutine.current_frame
                        current_frame.retire(values[0])
                    else:
                        return 0
            elif isinstance(term, bytecode.Goto):
                current_frame.goto(term.block_index)
            elif isinstance(term, bytecode.Conditional):
                v = current_frame.resolve_variable(term.condition_variable)
                assert isinstance(v, data.Bool)
                if v.b:
                    current_frame.goto(term.true_block)
                else:
                    current_frame.goto(term.false_block)
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
