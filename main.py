import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import bytecode.read
import bytecode.constructor
import bytecode.printer
import sys_calls
import execution.executor as executor
from rpython.rlib import rsocket
import data

data.register_all()

def entry_point(argv):
    rsocket.rsocket_startup()

    constructor = bytecode.constructor.BytecodeConstructor()

    with open(argv[1], 'r') as fd:
        bytecode.read.read_bytecode(fd, constructor)

    sys_caller = sys_calls.Perform()

    fd = None
    if len(argv) > 2:
        fd = open(argv[2], 'w')
        sys_caller = sys_calls.TraceProxy(sys_caller, fd)

    ex = executor.Executor(sys_caller, constructor.get_program())
    ex.run()

    if fd:
        fd.close()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
