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
                a = basic_block.constant(struct.pack('>B', 40))
                b = basic_block.constant(struct.pack('>B', 50))
                c = basic_block.syscall('add', [a, b])

                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/sub.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', []) as function:
            with function.basic_block() as basic_block:
                a = basic_block.constant(struct.pack('>B', 40))
                b = basic_block.constant(struct.pack('>B', 50))
                c = basic_block.syscall('sub', [a, b])

                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)

with open('bc/hello.bc', 'w') as fd:
    writer = bytecode_writer.BytecodeWriter(fd)

    with writer as program:
        with program.function('main', []) as function:
            with function.basic_block() as basic_block:
                basic_block.syscall('hello_world', [])
                v = basic_block.constant(struct.pack('>B', 0))
                basic_block.ret(v)
