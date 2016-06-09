import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import bytecode.read
import bytecode.constructor
import bytecode.printer
import execution.executor as executor

def entry_point(argv):
    constructor = bytecode.constructor.BytecodeConstructor()

    with open(argv[1], 'r') as fd:
        bytecode.read.read_bytecode(fd, constructor)

    ex = executor.Executor(constructor.get_program())
    ex.run()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
