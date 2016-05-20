#!/bin/bash
set -e;
source config.sh;
python ./write_out.py;
python ./main.py bc/hello.bc
