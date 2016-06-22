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

entry_module, modules = load_imports.load_imports(sys.argv[1])

module_interfaces = {}
for module_name, module in modules:
    type_checking.type_check_module(module_interfaces, module_name, module)

entry_service = evaluation.evaluate_entry_block(dict(modules), entry_module)
constructor = bytecode.constructor.BytecodeConstructor()
code_generation.generate_code(constructor, entry_service, dict(modules))

with open(sys.argv[2], 'w') as fd:
    writer = bytecode.writer.BytecodeWriter(fd)
    bytecode.serialize.serialize_program(writer, constructor.get_program())
