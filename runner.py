#!/usr/bin/env python

import sys

from primitives import CPUMem
from primitives import ALU
from cpus import RISC1
from io import Terminal

def load(fname):
    f = open(fname, 'rb')
    data = f.read()
    f.close()
    return data

def moveToMem(mem, data):
    i = 0
    for c in data:
        mem.setRaw(i, c)
        i += 1

def main():
    # 10k
    data = load(sys.argv[1])
    mainmem = CPUMem(1024*10)
    moveToMem(mainmem, data)

    term = Terminal()
    term.setBase(0x8010)

    mainmem.addSpecial(0x8000, None, term.setControl)
    mainmem.addSpecial(0x8001, None, term.setControl)
    mainmem.addSpecial(0x8002, None, term.setControl)
    mainmem.addSpecial(0x8003, None, term.setControl)
    for i in xrange(100):
        mainmem.addSpecial(0x8010 + i, term.getData, term.setData)

    cpu = RISC1(mainmem, ALU())
    cpu.start()

if __name__ == "__main__":
    main()