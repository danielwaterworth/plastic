import data
import sys_calls.ffi
import sys_calls.stdout
import sys_calls.socket

def sys_call(name, arguments):
    return data.sys_calls[name].call(arguments)
