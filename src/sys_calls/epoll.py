import data
import sys_calls.socket as s
from data import sys_call, expose_constant
from operators.list import DList
from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.tool import rffi_platform
from rpython.rlib import _rsocket_rffi, rsocket, rgc
from rpython.rlib._rsocket_rffi import socketclose, FD_SETSIZE
from rpython.rlib.rarithmetic import intmask
from rpython.translator.tool.cbuild import ExternalCompilationInfo

eci = ExternalCompilationInfo(
    includes = ['sys/epoll.h']
)

class CConfig:
    _compilation_info_ = eci


CConfig.epoll_data = rffi_platform.Struct("union epoll_data", [
    ("fd", rffi.INT),
])
CConfig.epoll_event = rffi_platform.Struct("struct epoll_event", [
    ("events", rffi.UINT),
    ("data", CConfig.epoll_data)
])

public_symbols = dict.fromkeys([
    "EPOLLIN", "EPOLLOUT", "EPOLLPRI", "EPOLLERR", "EPOLLHUP",
    "EPOLLET", "EPOLLONESHOT", "EPOLLRDNORM", "EPOLLRDBAND",
    "EPOLLWRNORM", "EPOLLWRBAND", "EPOLLMSG"
    ])
for symbol in public_symbols:
    setattr(CConfig, symbol, rffi_platform.DefinedConstantInteger(symbol))

for symbol in ["EPOLL_CTL_ADD", "EPOLL_CTL_MOD", "EPOLL_CTL_DEL"]:
    setattr(CConfig, symbol, rffi_platform.ConstantInteger(symbol))

cconfig = rffi_platform.configure(CConfig)

for symbol in public_symbols:
    public_symbols[symbol] = intmask(cconfig[symbol])

epoll_event = cconfig["epoll_event"]
EPOLL_CTL_ADD = cconfig["EPOLL_CTL_ADD"]
EPOLL_CTL_MOD = cconfig["EPOLL_CTL_MOD"]
EPOLL_CTL_DEL = cconfig["EPOLL_CTL_DEL"]

DEF_REGISTER_EVENTMASK = (public_symbols["EPOLLIN"] |
                          public_symbols["EPOLLOUT"] |
                          public_symbols["EPOLLPRI"])

epoll_create1 = rffi.llexternal(
    "epoll_create1", [rffi.INT], rffi.INT, compilation_info=eci,
    save_err=rffi.RFFI_SAVE_ERRNO
)
epoll_ctl = rffi.llexternal(
    "epoll_ctl",
    [rffi.INT, rffi.INT, rffi.INT, lltype.Ptr(epoll_event)],
    rffi.INT,
    compilation_info=eci,
    save_err=rffi.RFFI_SAVE_ERRNO
)
epoll_wait = rffi.llexternal(
    "epoll_wait",
    [rffi.INT, rffi.CArrayPtr(epoll_event), rffi.INT, rffi.INT],
    rffi.INT,
    compilation_info=eci,
    save_err=rffi.RFFI_SAVE_ERRNO
)

for key, value in public_symbols.iteritems():
    assert value >= 0
    expose_constant(key.lower(), data.UInt(value))

class EPoll(data.Data):
    def __init__(self):
        self.fd = epoll_create1(0)
        self.sockets = {}
        if self.fd < 0:
            raise rsocket.last_error()

    @rgc.must_be_light_finalizer
    def __del__(self):
        fd = self.fd
        if fd != _rsocket_rffi.INVALID_SOCKET:
            self.fd = _rsocket_rffi.INVALID_SOCKET
            _rsocket_rffi.socketclose_no_errno(fd)

    def register_sock(self, sock, flags):
        assert isinstance(sock, s.Socket)
        assert isinstance(flags, data.UInt)
        self.sockets[sock.fd] = sock
        with lltype.scoped_alloc(epoll_event) as ev:
            ev.c_events = rffi.cast(rffi.UINT, flags.n)
            rffi.setintfield(ev.c_data, 'c_fd', sock.fd)
            if epoll_ctl(self.fd, EPOLL_CTL_ADD, sock.fd, ev) < 0:
                raise rsocket.last_error()

    def unregister_sock(self, sock):
        assert isinstance(sock, s.Socket)
        del self.sockets[sock.fd]
        with lltype.scoped_alloc(epoll_event) as ev:
            ev.c_events = rffi.cast(rffi.UINT, 0)
            rffi.setintfield(ev.c_data, 'c_fd', sock.fd)
            if epoll_ctl(self.fd, EPOLL_CTL_DEL, sock.fd, ev) < 0:
                raise rsocket.last_error()

    def poll(self):
        timeout = -1
        maxevents = FD_SETSIZE - 1

        with lltype.scoped_alloc(rffi.CArray(epoll_event), maxevents) as evs:
            nfds = epoll_wait(self.fd, evs, maxevents, timeout)
            if nfds < 0:
                raise rsocket.last_error()

            output = [None] * nfds
            for i in xrange(nfds):
                event = evs[i]
                sock = self.sockets[event.c_data.c_fd]
                output[i] = DList([sock, data.UInt(event.c_events)])
            return DList(output)

@sys_call('epoll')
def call(self, arguments):
    assert len(arguments) == 0
    return EPoll()

@sys_call('epoll_register')
def call(self, arguments):
    epoll, sock, flags = arguments
    assert isinstance(epoll, EPoll)
    epoll.register_sock(sock, flags)
    return data.Void()

@sys_call('epoll_unregister')
def call(self, arguments):
    epoll, sock = arguments
    assert isinstance(epoll, EPoll)
    epoll.unregister_sock(sock)
    return data.Void()

@sys_call('epoll_poll')
def call(self, arguments):
    assert len(arguments) == 1
    epoll = arguments[0]
    assert isinstance(epoll, EPoll)
    return epoll.poll()
