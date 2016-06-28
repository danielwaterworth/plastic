import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import sys_calls
import data

data.register_all()

with open(sys.argv[1]) as fd:
    trace = sys_calls.read_trace(fd)

for name, arguments, return_values in trace:
    print name, arguments, return_values
