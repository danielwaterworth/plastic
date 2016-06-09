import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import struct
import bytecode.writer as bytecode_writer

with open('bc/noop.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', []) as function:
            with function.basic_block() as basic_block:
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/add.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', []) as function:
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
        with program.function('main', []) as function:
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
        with program.function('foo', []) as function:
            with function.basic_block() as basic_block:
                basic_block.goto(1)

            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>Q', 100))
                basic_block.sys_call('print_num', [a])
                basic_block.goto(1)

        with program.function('main', []) as function:
            with function.basic_block() as basic_block:
                basic_block.fun_call('foo', [])
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)
