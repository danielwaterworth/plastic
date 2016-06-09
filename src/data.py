from rpython.rlib.rstruct.runpack import runpack

def pack_uint(n):
    output = []
    for i in xrange(8):
        output.append(chr(n & 0xff))
        n = n >> 8
    return ''.join(reversed(output))

def sub(a, b):
    assert len(a) == 8
    assert len(b) == 8
    return pack_uint(runpack('>Q', a) - runpack('>Q', b))

def add(a, b):
    assert len(a) == 8
    assert len(b) == 8
    return pack_uint(runpack('>Q', a) + runpack('>Q', b))

def lt(a, b):
    assert len(a) == 8
    assert len(b) == 8
    return pack_uint(runpack('>Q', a) < runpack('>Q', b))
