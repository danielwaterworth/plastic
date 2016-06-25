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

def print_usage(prog):
    print "usage:"
    print "  %s exec BYTECODE" % prog
    print "  %s trace BYTECODE TRACE" % prog
    print "  %s replay BYTECODE TRACE" % prog

def entry_point(argv):
    rsocket.rsocket_startup()

    constructor = bytecode.constructor.BytecodeConstructor()

    fd = None
    if len(argv) < 3:
        print_usage(argv[0])
        return 1

    mode = argv[1]
    if mode == 'exec':
        sys_caller = sys_calls.Perform()
    elif mode == 'trace' and len(argv) == 4:
        fd = open(argv[3], 'w')
        sys_caller = sys_calls.TraceProxy(sys_calls.Perform(), fd)
    elif mode == 'replay' and len(argv) == 4:
        fd = open(argv[3], 'r')
        sys_caller = sys_calls.Replay(fd)
    else:
        print_usage(argv[0])
        return 1

    with open(argv[2], 'r') as fd:
        bytecode.read.read_bytecode(fd, constructor)

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
