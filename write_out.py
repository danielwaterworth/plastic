import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import struct
import bytecode.writer as bytecode_writer
import bytecode.printer as bytecode_printer

with open('bc/noop.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/add.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 40))
                b = basic_block.constant(struct.pack('>Q', 50))
                c = basic_block.sys_call('add', [a, b])
                basic_block.sys_call('print_num', [c])

                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/sub.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 50))
                b = basic_block.constant(struct.pack('>Q', 40))
                c = basic_block.sys_call('sub', [a, b])
                basic_block.sys_call('print_num', [c])

                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/hello.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('foo', 0) as (function, _):
            with function.basic_block() as basic_block:
                basic_block.goto(1)

            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 100))
                basic_block.sys_call('print_num', [a])
                basic_block.goto(1)

        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                basic_block.fun_call('foo', [])
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/function_call.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('foo', 1) as (function, [a]):
            with function.basic_block() as basic_block:
                basic_block.sys_call('print_num', [a])

                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 100))
                basic_block.fun_call('foo', [a])
                
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/condition.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 40))
                b = basic_block.constant(struct.pack('>Q', 50))
                c = basic_block.sys_call('lt', [a, b])
                basic_block.conditional(c, 1, 2)

            with function.basic_block() as basic_block:
                v = basic_block.constant(struct.pack('>Q', 1))
                basic_block.sys_call('print_num', [v])
                basic_block.goto(3)

            with function.basic_block() as basic_block:
                v = basic_block.constant(struct.pack('>Q', 2))
                basic_block.sys_call('print_num', [v])
                basic_block.goto(3)

            with function.basic_block() as basic_block:
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/loop.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 0))
                b = basic_block.constant(struct.pack('>Q', 1))
                c = basic_block.constant(struct.pack('>Q', 4))
                basic_block.goto(1)

            with function.basic_block() as basic_block:
                i_next = basic_block.forward()
                i = basic_block.phi([(0, a), (1, i_next)])
                i_next.assign(basic_block.sys_call('add', [i, b]))
                c = basic_block.sys_call('lt', [i_next, c])
                basic_block.sys_call('print_num', [i])
                basic_block.conditional(c, 1, 2)

            with function.basic_block() as basic_block:
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/store_load.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', 0) as (function, _):
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 100))
                b = basic_block.constant(struct.pack('>Q', 42))
                basic_block.store(a, b)
                c = basic_block.load(a)
                basic_block.sys_call('print_num', [c])
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)
