#!/bin/bash
source ./config.sh;
python $PYPY_INSTALL/rpython/bin/rpython ./main.py;
