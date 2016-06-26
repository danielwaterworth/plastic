import data
from data import sys_call
from rpython.rlib import rsocket
from rpython.rlib.rarithmetic import intmask, r_ulonglong
from rpython.rlib.rstruct.runpack import runpack

class Socket(data.Data):
    def __init__(self, sock, fd=-1):
        self.sock = sock
        if self.sock:
            self.fd = self.sock.fd
        else:
            self.fd = fd

    def persist(self, fd):
        fd.write(self.type_id)
        fd.write(data.pack_int(self.fd))

    @staticmethod
    def load(fd):
        n = runpack('>q', fd.read(8))
        return Socket(None, n)

    def __repr__(self):
        return '(socket %s)' % self.fd

    def eq(self, other):
        return isinstance(other, Socket) and self.fd == other.fd

@sys_call('socket_socket')
def call(self, arguments):
    family, type, proto = arguments
    assert isinstance(family, data.UInt)
    assert isinstance(type, data.UInt)
    assert isinstance(proto, data.UInt)
    return Socket(rsocket.RSocket(intmask(family.n), intmask(type.n), intmask(proto.n)))

@sys_call('socket_bind')
def call(self, arguments):
    socket, address, port = arguments
    assert isinstance(socket, Socket)
    assert isinstance(address, data.String)
    assert isinstance(port, data.UInt)
    socket.sock.bind(rsocket.INETAddress(address.v.encode('utf-8'), intmask(port.n)))
    return data.Void()

@sys_call('socket_listen')
def call(self, arguments):
    socket, backlog = arguments
    assert isinstance(socket, Socket)
    assert isinstance(backlog, data.UInt)
    socket.sock.listen(backlog.n)
    return data.Void()

@sys_call('socket_accept')
def call(self, arguments):
    assert len(arguments) == 1
    socket = arguments[0]
    assert isinstance(socket, Socket)
    s, _ = socket.sock.accept()
    return Socket(rsocket.RSocket(fd=s))

@sys_call('socket_recv')
def call(self, arguments):
    socket, n = arguments
    assert isinstance(socket, Socket)
    assert isinstance(n, data.UInt)
    return data.ByteString(socket.sock.recv(intmask(n.n)))

@sys_call('socket_send')
def call(self, arguments):
    socket, dat = arguments
    assert isinstance(socket, Socket)
    assert isinstance(dat, data.ByteString)
    socket.sock.sendall(dat.v)
    return data.Void()

@sys_call('socket_close')
def call(self, arguments):
    assert len(arguments) == 1
    socket = arguments[0]
    assert isinstance(socket, Socket)
    socket.sock.close()
    return data.Void()
