import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import bytecode.read
import bytecode.constructor
import bytecode.printer
import sys_calls
import execution.executor as executor
from rpython.rlib import rsocket, rsignal
import data
import operators.list

data.register_all()

def print_usage(prog):
    print "usage:"
    print "  %s exec BYTECODE" % prog
    print "  %s trace TRACE BYTECODE" % prog
    print "  %s replay TRACE BYTECODE" % prog

def entry_point(argv):
    rsignal.pypysig_setflag(rsignal.SIGINT)
    rsocket.rsocket_startup()

    constructor = bytecode.constructor.BytecodeConstructor()

    if len(argv) < 3:
        print_usage(argv[0])
        return 1

    trace_fd = None
    mode = argv[1]
    if mode == 'exec':
        program = argv[2]
        argv = argv[2:]
        sys_caller = sys_calls.Perform(program)
    elif mode == 'trace' and len(argv) >= 4:
        program = argv[3]
        trace_fd = open(argv[2], 'w')
        argv = argv[3:]
        sys_caller = sys_calls.TraceProxy(sys_calls.Perform(program), trace_fd)
    elif mode == 'replay' and len(argv) >= 4:
        program = argv[3]
        argv = argv[3:]
        trace_fd = open(argv[2], 'r')
        sys_caller = sys_calls.Replay(trace_fd)
    else:
        print_usage(argv[0])
        return 1

    with open(program, 'r') as fd:
        bytecode.read.read_bytecode(fd, constructor)

    arguments = [operators.list.DList([data.ByteString(arg) for arg in argv])]

    try:
        ex = executor.Executor(sys_caller, constructor.get_program(), arguments)
        ex.run()
    finally:
        if trace_fd:
            trace_fd.close()

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
