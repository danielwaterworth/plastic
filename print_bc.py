import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import bytecode.printer
import bytecode.read

with open(sys.argv[1]) as fd:
    bytecode.read.read_bytecode(fd, bytecode.printer.BytecodePrinter())
