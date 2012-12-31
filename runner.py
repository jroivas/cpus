#!/usr/bin/env python

import sys

from primitives import Mem
from primitives import ALU
from primitives import Clock
from cpus import RISC1
from sysio import Terminal

if sys.version >= '3':
    xrange = range

def fileLoad(fname):
    f = open(fname, 'rb')
    header_size = 12
    header = f.read(header_size)
    if header[:4] != b'RE01':
        f.close()
        return None

    tmp = header[4:8]
    datapos = 0
    for i in reversed(tmp):
        if sys.version < '3':
            datapos |= ord(i)
        else:
            datapos |= i
        datapos <<= 8
    datapos >>= 8

    tmp = header[8:]
    basepos = 0
    for i in reversed(tmp):
        if sys.version < '3':
            basepos |= ord(i)
        else:
            basepos |= i
        basepos <<= 8
    basepos >>= 8

    code = f.read(datapos - header_size)
    data = f.read()
    f.close()

    return (code, data, basepos)

def moveToMem(mem, data, i=None):
    if i is None:
        i = 0
    for c in data:
        mem.setRaw(i, c)
        i += 1

def main():
    (code, data, base) = fileLoad(sys.argv[1])

    mainmem = Mem(len(code) + len(data))
    moveToMem(mainmem, code)
    if base > 0 and len(code) < base:
        tmp = Mem(base - len(code))
        mainmem.append(tmp)
    moveToMem(mainmem, data, base)

    term = Terminal()
    term.setBase(0x8010)

    mainmem.addSpecial(0x8000, None, term.setControl)
    mainmem.addSpecial(0x8001, None, term.setControl)
    mainmem.addSpecial(0x8002, None, term.setControl)
    mainmem.addSpecial(0x8003, None, term.setControl)
    for i in xrange(100):
        mainmem.addSpecial(0x8010 + i, term.getData, term.setData)

    cpu = RISC1(mainmem, ALU())
    clock = Clock(hz=1000, callfunc=cpu.raiseInterrupt, params=1)
    clock.start()
    try:
        cpu.start()
    except:
        clock.stop()
        raise
    clock.stop()

if __name__ == "__main__":
    main()
