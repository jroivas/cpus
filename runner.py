#!/usr/bin/env python

import sys

from primitives import Mem
from primitives import ALU
from primitives import Clock
from cpus import RISC1
from io import Terminal

def load(fname):
    f = open(fname, 'rb')
    header = f.read(8)
    if header[:4] != 'RE01':
        f.close()
        return None
    tmp = header[4:]
    datapos = 0
    for i in reversed(tmp):
        datapos |= ord(i)
        datapos <<= 8
    datapos >>= 8
    code = f.read(datapos - 8)
    data = f.read()
    f.close()
    return (code, data)

def moveToMem(mem, data):
    i = 0
    for c in data:
        mem.setRaw(i, c)
        i += 1

def main():
    (code, data) = load(sys.argv[1])

    codemem = Mem(len(code) + 4)
    # 10k
    mainmem = Mem(1024)
    moveToMem(codemem, code)
    moveToMem(mainmem, data)

    term = Terminal()
    term.setBase(0x8010)

    mainmem.addSpecial(0x8000, None, term.setControl)
    mainmem.addSpecial(0x8001, None, term.setControl)
    mainmem.addSpecial(0x8002, None, term.setControl)
    mainmem.addSpecial(0x8003, None, term.setControl)
    for i in xrange(100):
        mainmem.addSpecial(0x8010 + i, term.getData, term.setData)

    cpu = RISC1(codemem, mainmem, ALU())
    clock = Clock(hz=1000, callfunc=cpu.raiseInterrupt, params=1)
    clock.start()
    cpu.start()
    clock.stop()

if __name__ == "__main__":
    main()
