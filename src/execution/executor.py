from rpython.rlib.jit import JitDriver, hint, unroll_safe
import bytecode
import data
import operators
import pdb

@unroll_safe
def activation_record(function, arguments):
    assert function.num_arguments == len(arguments)
    values = arguments + [data.invalid for i in xrange(function.n_values)]
    last_block_index = 0
    current_block_index = 0
    pc = 0
    return ActivationFrame(values, function, last_block_index, current_block_index, pc)

def resolve_variable(values, var):
    value = values[var]
    assert not isinstance(value, data.Invalid)
    values[var] = data.invalid
    return value

@unroll_safe
def resolve_variable_list(values, variables):
    return [resolve_variable(values, var) for var in variables]

def next_instruction(function, current_block_index, pc):
    current_block = function.get_block(current_block_index)
    if current_block.num_instructions() <= pc:
        return None
    else:
        return current_block.get_instruction(pc)

def terminator(function, current_block_index):
    current_block = function.get_block(current_block_index)
    return current_block.terminator

def retire(values, function, current_block_index, pc, value):
    next_value = function.get_block_value_offset(current_block_index) + pc
    values[next_value] = value
    return (pc + 1)

@unroll_safe
def retire_multiple(values, function, current_block_index, pc, v):
    assert len(v) >= 1
    pc = retire(values, function, current_block_index, pc, v[0])
    for value in v[1:]:
        instr = next_instruction(function, current_block_index, pc)
        assert isinstance(instr, bytecode.Unpack)
        pc = retire(values, function, current_block_index, pc, value)
    return pc

def copy(values, function, current_block_index, pc):
    next_value = function.get_block_value_offset(current_block_index) + pc
    value = next_value - 1
    assert value >= 0
    return values[value].copy()

def goto(function, current_block_index, last_block_index, block):
    assert block < function.num_blocks()

    last_block_index = current_block_index
    current_block_index = block

    pc = 0
    return (last_block_index, current_block_index, pc)

class ActivationFrame(object):
    def __init__(self, values, function, last_block_index, current_block_index, pc):
        self.values = values
        self.function = function
        self.last_block_index = last_block_index
        self.current_block_index = current_block_index
        self.pc = pc

class Coroutine(data.Data):
    def __init__(self):
        self.stack = []
        self.done = False
        self.var = data.void

    def print_backtrace(self):
        print ''
        print 'backtrace:'
        for frame in self.stack:
            values = frame.values
            function = frame.function
            last_block_index = frame.last_block_index
            current_block_index = frame.current_block_index
            pc = frame.pc
            next_value = function.block_value_offsets[current_block_index] + pc
            print '  %s:%d' % (function.name, next_value)
        print ''

def get_location(current_block_index, last_block_index, pc, function, program, sys_caller):
    name = function.name
    value = function.get_block_value_offset(current_block_index) + pc
    instruction = str(next_instruction(function, current_block_index, pc))
    return "%s  :  %s  :  %s" % (name, value, instruction)

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
                    ],
                    get_printable_location=get_location
                )

def execute(sys_caller, program, arguments):
    coroutine_stack = []
    memory = [data.invalid] * 1024**2

    for function_name, function in program.functions.iteritems():
        block_value_offsets = []
        n_values = 0
        for block in function.blocks:
            block_value_offsets.append(function.num_arguments + n_values)
            n_values += block.num_instructions()

        function.n_values = n_values
        function.block_value_offsets = block_value_offsets

    coroutine = Coroutine()

    frame = activation_record(program.functions['$main'], arguments)
    values = frame.values
    function = frame.function
    last_block_index = frame.last_block_index
    current_block_index = frame.current_block_index
    pc = frame.pc
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
        instr = next_instruction(function, current_block_index, pc)
        if instr:
            if isinstance(instr, bytecode.Phi):
                value = resolve_variable(values, instr.get_input(last_block_index))
                pc = retire(values, function, current_block_index, pc, value)
            elif isinstance(instr, bytecode.Copy):
                value = copy(values, function, current_block_index, pc)
                pc = retire(values, function, current_block_index, pc, value)
            elif isinstance(instr, bytecode.Move):
                value = resolve_variable(values, instr.variable)
                pc = retire(values, function, current_block_index, pc, value)
            elif isinstance(instr, bytecode.Operation):
                arguments = resolve_variable_list(values, instr.arguments)
                if instr.operator == 'is_done':
                    assert len(instr.arguments) == 1
                    c = arguments[0]
                    assert isinstance(c, Coroutine)
                    value = data.Bool(c.done)
                    pc = retire(values, function, current_block_index, pc, value)
                else:
                    operator = operators.operator(instr.operator)
                    v = operator.call(arguments)
                    pc = retire_multiple(values, function, current_block_index, pc, v)
            elif isinstance(instr, bytecode.SysCall):
                arguments = resolve_variable_list(values, instr.arguments)
                v = sys_caller.sys_call(instr.function, arguments)
                pc = retire_multiple(values, function, current_block_index, pc, v)
            elif isinstance(instr, bytecode.FunctionCall):
                arguments = resolve_variable_list(values, instr.arguments)
                coroutine.stack.append(ActivationFrame(values, function, last_block_index, current_block_index, pc))
                frame = activation_record(program.get_function(instr.function), arguments)
                values = frame.values
                function = frame.function
                last_block_index = frame.last_block_index
                current_block_index = frame.current_block_index
                pc = frame.pc
            elif isinstance(instr, bytecode.NewCoroutine):
                arguments = resolve_variable_list(values, instr.arguments)
                f = program.get_function(instr.function)
                c = Coroutine()
                c.stack.append(activation_record(f, arguments))
                pc = retire(values, function, current_block_index, pc, c)
            elif isinstance(instr, bytecode.Debug):
                value = resolve_variable(values, instr.value)
                print value.debug()
                pc = retire(values, function, current_block_index, pc, data.void)
            elif isinstance(instr, bytecode.ConstantBool):
                pc = retire(values, function, current_block_index, pc, data.Bool(instr.value))
            elif isinstance(instr, bytecode.ConstantByte):
                pc = retire(values, function, current_block_index, pc, data.Byte(instr.value))
            elif isinstance(instr, bytecode.ConstantChar):
                pc = retire(values, function, current_block_index, pc, data.Char(instr.value))
            elif isinstance(instr, bytecode.ConstantByteString):
                pc = retire(values, function, current_block_index, pc, data.ByteString(instr.value))
            elif isinstance(instr, bytecode.ConstantString):
                pc = retire(values, function, current_block_index, pc, data.String(instr.value))
            elif isinstance(instr, bytecode.ConstantInt):
                pc = retire(values, function, current_block_index, pc, data.Int(instr.value))
            elif isinstance(instr, bytecode.ConstantUInt):
                pc = retire(values, function, current_block_index, pc, data.UInt(instr.value))
            elif isinstance(instr, bytecode.ConstantDouble):
                pc = retire(values, function, current_block_index, pc, data.Double(instr.value))
            elif isinstance(instr, bytecode.Void):
                pc = retire(values, function, current_block_index, pc, data.void)
            elif isinstance(instr, bytecode.Load):
                address = resolve_variable(values, instr.address)
                assert isinstance(address, data.UInt)
                dat = memory[address.n]
                pc = retire(values, function, current_block_index, pc, dat)
            elif isinstance(instr, bytecode.Store):
                address = resolve_variable(values, instr.address)
                value = resolve_variable(values, instr.variable)
                assert isinstance(address, data.UInt)
                memory[address.n] = value
                pc = retire(values, function, current_block_index, pc, data.void)
            elif isinstance(instr, bytecode.Get):
                pc = retire(values, function, current_block_index, pc, coroutine.var)
            elif isinstance(instr, bytecode.Put):
                coroutine.var = resolve_variable(values, instr.variable)
                pc = retire(values, function, current_block_index, pc, data.void)
            elif isinstance(instr, bytecode.RunCoroutine):
                c = resolve_variable(values, instr.coroutine)
                assert isinstance(c, Coroutine)
                coroutine.stack.append(ActivationFrame(values, function, last_block_index, current_block_index, pc))
                coroutine_stack.append(coroutine)
                coroutine = c
                frame = coroutine.stack.pop()
                values = frame.values
                function = frame.function
                last_block_index = frame.last_block_index
                current_block_index = frame.current_block_index
                pc = frame.pc
            elif isinstance(instr, bytecode.Yield):
                value = resolve_variable(values, instr.value)
                if coroutine_stack:
                    coroutine.stack.append(ActivationFrame(values, function, last_block_index, current_block_index, pc))
                    coroutine = coroutine_stack.pop()
                    frame = coroutine.stack.pop()
                    values = frame.values
                    function = frame.function
                    last_block_index = frame.last_block_index
                    current_block_index = frame.current_block_index
                    pc = frame.pc
                    pc = retire(values, function, current_block_index, pc, value)
                else:
                    raise Exception('yielded from top level coroutine')
            elif isinstance(instr, bytecode.Resume):
                c = resolve_variable(values, instr.coroutine)
                assert isinstance(c, Coroutine)
                value = resolve_variable(values, instr.value)

                coroutine.stack.append(ActivationFrame(values, function, last_block_index, current_block_index, pc))
                coroutine_stack.append(coroutine)
                coroutine = c
                frame = coroutine.stack.pop()
                values = frame.values
                function = frame.function
                last_block_index = frame.last_block_index
                current_block_index = frame.current_block_index
                pc = frame.pc
                pc = retire(values, function, current_block_index, pc, value)
            else:
                raise NotImplementedError('missing instruction implementation')
        else:
            term = terminator(function, current_block_index)
            if isinstance(term, bytecode.Return):
                v = resolve_variable_list(values, term.variables)

                if coroutine.stack:
                    frame = coroutine.stack.pop()
                    values = frame.values
                    function = frame.function
                    last_block_index = frame.last_block_index
                    current_block_index = frame.current_block_index
                    pc = frame.pc
                    pc = retire_multiple(values, function, current_block_index, pc, v)
                else:
                    assert len(v) == 1
                    coroutine.done = True

                    if coroutine_stack:
                        coroutine = coroutine_stack.pop()
                        frame = coroutine.stack.pop()
                        values = frame.values
                        function = frame.function
                        last_block_index = frame.last_block_index
                        current_block_index = frame.current_block_index
                        pc = frame.pc
                        pc = retire(values, function, current_block_index, pc, v[0])
                    else:
                        return 0
            elif isinstance(term, bytecode.Goto):
                last_block_index, current_block_index, pc = goto(function, current_block_index, last_block_index, term.block_index)
            elif isinstance(term, bytecode.Conditional):
                v = resolve_variable(values, term.condition_variable)
                assert isinstance(v, data.Bool)
                if v.b:
                    last_block_index, current_block_index, pc = goto(function, current_block_index, last_block_index, term.true_block)
                else:
                    last_block_index, current_block_index, pc = goto(function, current_block_index, last_block_index, term.false_block)
            elif isinstance(term, bytecode.CatchFireAndDie):
                coroutine.stack.append(ActivationFrame(values, function, last_block_index, current_block_index, pc))
                coroutine.print_backtrace()
                raise Exception('catching fire and dying')
            elif isinstance(term, bytecode.Throw):
                coroutine.stack.append(ActivationFrame(values, function, last_block_index, current_block_index, pc))
                coroutine.print_backtrace()
                exception = resolve_variable(values, term.exception)
                print exception
                raise Exception('throw')
            else:
                raise NotImplementedError('missing terminator implementation')
