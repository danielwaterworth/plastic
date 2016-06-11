import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'compiler'))
import struct
import parse

with open(sys.argv[1], 'r') as fd:
    source = fd.read()

parse.parser.parse(source)
