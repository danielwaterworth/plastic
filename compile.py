import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import parse
    import type_checking
    import evaluation
    import code_generation
    import bytecode.serialize
    import bytecode.constructor
    import bytecode.optimizer
    import bytecode.writer
    import load_imports

    lib_dir = os.path.join(os.path.dirname(__file__), 'lib')

    entry_module, modules = load_imports.load_imports(lib_dir, sys.argv[1])

    module_interfaces = {}
    for module_name, module in modules:
        type_checking.type_check_module(module_interfaces, module_name, module)

    modules = dict(modules)
    constructor = bytecode.constructor.BytecodeConstructor()
    with constructor as writer:
        for module in modules.itervalues():
            code_generation.generate_module(writer, module)

        entry_service = evaluation.evaluate_entry_block(modules, entry_module)
        code_generation.generate_entry(writer, entry_service, modules)

    with open(sys.argv[2], 'w') as fd:
        writer = bytecode.writer.BytecodeWriter(fd)
        bytecode.serialize.serialize_program(writer, constructor.get_program())
except:
    import traceback
    import pdb
    traceback.print_exc()
    print ''
    pdb.post_mortem()
    sys.exit(1)
