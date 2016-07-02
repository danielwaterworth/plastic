#!/bin/bash
source ./config.sh;
python $PYPY_INSTALL/rpython/bin/rpython --opt=jit ./main.py;
