import data
from data import sys_call

@sys_call('print_string')
def call(self, arguments):
    assert len(arguments) == 1
    a = arguments[0]
    assert isinstance(a, data.String)
    print a.v
    return data.Void()

@sys_call('print_uint')
def call(self, arguments):
    assert len(arguments) == 1
    a = arguments[0]
    assert isinstance(a, data.UInt)
    print a.n
    return data.Void()

@sys_call('print_bool')
def call(self, arguments):
    assert len(arguments) == 1
    a = arguments[0]
    assert isinstance(a, data.Bool)
    if a.b:
        print 'True'
    else:
        print 'False'
    return data.Void()

@sys_call('print_char')
def call(self, arguments):
    assert len(arguments) == 1
    a = arguments[0]
    assert isinstance(a, data.Char)
    print a.b
    return data.Void()
