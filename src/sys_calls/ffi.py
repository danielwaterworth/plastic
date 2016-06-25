import data
from data import sys_call
import rpython.rlib.clibffi as ffi
from operators.list import DList
from rpython.rtyper.lltypesystem import rffi, lltype

class DLib(data.Data):
    def __init__(self, lib):
        self.lib = lib

class DForeignPtr(data.Data):
    def __init__(self, ptr):
        self.ptr = ptr

class DForeignFunction(data.Data):
    def __init__(self, foreign_function, arg_types, ret_type):
        self.foreign_function = foreign_function
        self.arg_types = arg_types
        self.ret_type = ret_type

class DType(data.Data):
    def __init__(self, ty):
        self.ty = ty

class DStructType(DType):
    def __init__(self, tys):
        self.struct = ffi.make_struct_ffitype_e(0, 0, tys)
        self.ty = self.struct.ffistruct

    def __del__(self):
        lltype.free(self.struct, flavor='raw')

@sys_call('ffi.get_libc_name')
def call(self, arguments):
    assert len(arguments) == 0
    return data.ByteString(ffi.get_libc_name())

@sys_call('ffi.get_lib')
def call(self, arguments):
    assert len(arguments) == 1
    name = arguments[0]
    assert isinstance(name, data.ByteString)
    return DLib(ffi.CDLL(name.v))

@sys_call('ffi.get_pointer')
def call(self, arguments):
    lib, name, arg_types, ret_type = arguments
    assert isinstance(lib, DLib)
    assert isinstance(name, data.ByteString)
    assert isinstance(arg_types, DList)
    assert isinstance(ret_type, DType)
    args = []
    copied_types = []
    for arg_type in arg_types.elements:
        assert isinstance(arg_type, DType)
        args.append(arg_type.ty)
        copied_types.append(arg_type)
    f = lib.lib.getpointer(name.v, args, ret_type.ty)
    return DForeignFunction(f, copied_types, ret_type)

for name in ffi.base_names:
    value = DType(getattr(ffi, 'ffi_type_%s' % name))
    ffi_name = 'ffi.%s' % name
    data.ExposeConstant(ffi_name, value).register()

@sys_call('ffi.struct_type')
def call(self, arguments):
    assert len(arguments) == 1
    types = arguments[0]
    assert isinstance(types, DList)
    ffi_types = []
    for ty in types.elements:
        assert isinstance(ty, DType)
        ffi_types.append(ty.ty)
    return DStructType(ffi_types)

@sys_call('ffi.call')
def call(self, arguments):
    function, args = arguments
    assert isinstance(function, DForeignFunction)
    assert isinstance(args, DList)
    assert len(function.arg_types) == len(args.elements)
    for i in xrange(len(function.arg_types)):
        ty = function.arg_types[i]
        arg = args.elements[i]
        if ty.ty == ffi.ffi_type_pointer:
            assert isinstance(arg, DForeignPtr)
            function.foreign_function.push_arg(arg.ptr)
        elif ty.ty == ffi.ffi_type_sint:
            assert isinstance(arg, data.Int)
            function.foreign_function.push_arg(arg.n)
        else:
            raise TypeError()
    if function.ret_type.ty == ffi.ffi_type_pointer:
        ptr = function.foreign_function.call(rffi.VOIDP)
        return DForeignPtr(ptr)
    elif function.ret_type.ty == ffi.ffi_type_sint:
        n = function.foreign_function.call(rffi.LONG)
        return data.Int(n)
    else:
        raise TypeError()
