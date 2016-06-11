import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import code_generation
import parse
import bytecode.writer

with open(sys.argv[1], 'r') as fd:
    source = fd.read()

with open(sys.argv[2], 'w') as fd:
    writer = bytecode.writer.BytecodeWriter(fd)
    ast = parse.parser.parse(source)

    code_generation.generate_code(writer, ast)
