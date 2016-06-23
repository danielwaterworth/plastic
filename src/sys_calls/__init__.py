import data
import sys_calls.ffi
import sys_calls.stdout

def sys_call(name, arguments):
    return data.sys_calls[name].call(arguments)
