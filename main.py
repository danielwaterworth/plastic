import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import bytecode_read
import bytecode_printer

def entry_point(argv):
    with open('bc/noop.bc') as fd:
        bytecode_read.read_bytecode(fd, bytecode_printer.BytecodePrinter())
    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    import sys
    entry_point(sys.argv)
