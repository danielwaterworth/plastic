#!/bin/bash
source ./config.sh;
python $PYPY_INSTALL/rpython/bin/rpython ./write_out.py;
