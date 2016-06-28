import os
import data
from rpython.rlib.rarithmetic import intmask
from data import sys_call

class File(data.Data):
    def __init__(self, fd):
        self.fd = fd

@sys_call('file_open')
def call(self, arguments):
    filename, mode = arguments
    assert isinstance(filename, data.ByteString)
    assert isinstance(mode, data.UInt)
    fd = os.open(filename.v, intmask(mode.n), 0777)
    assert fd >= 0
    return [File(fd)]

@sys_call('file_read')
def call(self, arguments):
    file, n = arguments
    assert isinstance(file, File)
    assert isinstance(n, data.UInt)
    return [data.ByteString(os.read(file.fd, intmask(n.n)))]

@sys_call('file_write')
def call(self, arguments):
    file, dat = arguments
    assert isinstance(file, File)
    assert isinstance(dat, data.ByteString)
    os.write(file.fd, dat.v)
    return [data.Void()]

@sys_call('file_close')
def call(self, arguments):
    assert len(arguments) == 1
    file = arguments[0]
    assert isinstance(file, File)
    os.close(file.fd)
    return [data.Void()]

