import data
import sys_calls.ffi
import sys_calls.stdout

def sys_call(name, arguments):
    if name in data.sys_calls:
        return data.sys_calls[name].call(arguments)
    elif name == 'print_num':
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.UInt)
        print a.n
        return data.Void()
    elif name == 'print_bool':
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.Bool)
        if a.b:
            print 'True'
        else:
            print 'False'
        return data.Void()
    elif name == 'print_char':
        assert len(arguments) == 1
        a = arguments[0]
        assert isinstance(a, data.Char)
        print a.b
        return data.Void()
    else:
        raise NotImplementedError('sys_call not implemented: %s' % name)
