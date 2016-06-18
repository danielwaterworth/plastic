import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import parse
import type_checking
import evaluation
import code_generation
import bytecode.serialize
import bytecode.constructor
import bytecode.writer

with open(sys.argv[1], 'r') as fd:
    source = fd.read()

ast = parse.parser.parse(source)
type_checking.type_check(ast)
entry_service = evaluation.evaluate_entry_block(ast)
constructor = bytecode.constructor.BytecodeConstructor()
code_generation.generate_code(constructor, entry_service, ast)

with open(sys.argv[2], 'w') as fd:
    writer = bytecode.writer.BytecodeWriter(fd)
    bytecode.serialize.serialize_program(writer, constructor.get_program())
