import data
from rpython.rlib import rsocket
from rpython.rlib.rarithmetic import intmask, r_ulonglong
from rpython.rlib.rstruct.runpack import runpack

class Socket(data.Data):
    def __init__(self, sock, fd=None):
        self.sock = sock
        self.fd = fd

    def persist(self, fd):
        fd.write(self.type_id)
        if self.sock:
            n = self.sock.fd
        else:
            n = self.fd
        assert n
        fd.write(data.pack_int(n))

    @classmethod
    def load(cls, fd):
        n = runpack('>q', fd.read(8))
        return cls(None, n)

    def __repr__(self):
        if self.sock:
            return '(socket %s)' % self.sock.fd
        else:
            return '(socket %s)' % self.fd

class SocketSysCall(data.SysCall):
    def __init__(self):
        self.name = 'socket_socket'

    def call(self, arguments):
        family, type, proto = arguments
        assert isinstance(family, data.UInt)
        assert isinstance(type, data.UInt)
        assert isinstance(proto, data.UInt)
        return Socket(rsocket.RSocket(intmask(family.n), intmask(type.n), intmask(proto.n)))

SocketSysCall().register()

class Bind(data.SysCall):
    def __init__(self):
        self.name = 'socket_bind'

    def call(self, arguments):
        socket, address, port = arguments
        assert isinstance(socket, Socket)
        assert isinstance(address, data.String)
        assert isinstance(port, data.UInt)
        socket.sock.bind(rsocket.INETAddress(address.v.encode('utf-8'), intmask(port.n)))
        return data.Void()

Bind().register()

class Listen(data.SysCall):
    def __init__(self):
        self.name = 'socket_listen'

    def call(self, arguments):
        socket, backlog = arguments
        assert isinstance(socket, Socket)
        assert isinstance(backlog, data.UInt)
        socket.sock.listen(backlog.n)
        return data.Void()

Listen().register()

class Accept(data.SysCall):
    def __init__(self):
        self.name = 'socket_accept'

    def call(self, arguments):
        assert len(arguments) == 1
        socket = arguments[0]
        assert isinstance(socket, Socket)
        s, _ = socket.sock.accept()
        return Socket(rsocket.RSocket(fd=s))

Accept().register()

class Recv(data.SysCall):
    def __init__(self):
        self.name = 'socket_recv'

    def call(self, arguments):
        socket, n = arguments
        assert isinstance(socket, Socket)
        assert isinstance(n, data.UInt)
        return data.ByteString(socket.sock.recv(intmask(n.n)))

Recv().register()

class Send(data.SysCall):
    def __init__(self):
        self.name = 'socket_send'

    def call(self, arguments):
        socket, dat = arguments
        assert isinstance(socket, Socket)
        assert isinstance(dat, data.ByteString)
        socket.sock.sendall(dat.v)
        return data.Void()

Send().register()

class Close(data.SysCall):
    def __init__(self):
        self.name = 'socket_close'

    def call(self, arguments):
        assert len(arguments) == 1
        socket = arguments[0]
        assert isinstance(socket, Socket)
        socket.sock.close()
        return data.Void()

Close().register()
