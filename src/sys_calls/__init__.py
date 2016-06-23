import data
import sys_calls.ffi
import sys_calls.stdout
import sys_calls.socket
from rpython.rlib.rstruct.runpack import runpack

class SysCallInterface(object):
    def sys_call(self, name, arguments):
        raise NotImplementedError()

class Perform(SysCallInterface):
    def sys_call(self, name, arguments):
        return data.sys_calls[name].call(arguments)

class TraceProxy(SysCallInterface):
    def __init__(self, target, fd):
        self.target = target
        self.fd = fd

    def sys_call(self, name, arguments):
        value = self.target.sys_call(name, arguments)

        self.fd.write(data.pack_uint(len(name)))
        self.fd.write(name)
        self.fd.write(data.pack_uint(len(arguments)))
        for arg in arguments:
            arg.persist(self.fd)
        value.persist(self.fd)

        return value

class Reply(SysCallInterface):
    def __init__(self, trace):
        self.trace = trace

    def sys_call(self, name, arguments):
        expected_name, expected_arguments, return_value = self.trace.pop()
        assert expected_name == name
        assert expected_arguments == arguments
        return return_value

def read_trace(fd):
    trace = []
    try:
        while True:
            b = fd.read(8)
            if not b:
                break
            n = runpack('>Q', b)
            name = fd.read(n)
            n = runpack('>Q', fd.read(8))
            arguments = [data.load(fd) for i in xrange(n)]
            return_value = data.load(fd)
            trace.append((name, arguments, return_value))
    except:
        pass
    return trace
