import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))
import struct
import lexer

with open(sys.argv[1], 'r') as fd:
    source = fd.read()

lexer.lexer.input(source)

for token in lexer.lexer:
    print token
