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
import load_imports

entry_module, ast = load_imports.load_imports(sys.argv[1])
type_checking.type_check(ast)
entry_service = evaluation.evaluate_entry_block(ast, entry_module)
constructor = bytecode.constructor.BytecodeConstructor()
code_generation.generate_code(constructor, entry_service, ast)

with open(sys.argv[2], 'w') as fd:
    writer = bytecode.writer.BytecodeWriter(fd)
    bytecode.serialize.serialize_program(writer, constructor.get_program())
