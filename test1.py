#!/usr/bin/env python

import sys

from primitives import Mem
from primitives import ALU
from cpus import RISC1
from io import Terminal

def genInstruction(inst, imm):
    inst = inst & 0xFF
    imm = imm & 0xFFFFFF
    imm <<= 8
    return (inst | imm)

def genReg(x,y,i):
    x = (x+1) & 0xFF
    y = ((y+1) & 0xFF) << 8
    i = (i & 0xFF) << 16
    return (x | y | i)
        
def program(mem):
    index = 0

    mem.setData(index, genInstruction(0x01, 100) )
    mem.setData(100, 10)
    index += 4
    mem.setData(index, genInstruction(0x10, genReg(-1, -1, 5)) )
    index += 4
    mem.setData(index, genInstruction(0x05, genReg(1, 0, 8)) )
    index += 4
    mem.setData(index, genInstruction(0x05, genReg(2, -1, 16)) )
    index += 4
    mem.setData(index, genInstruction(0x07, genReg(2, 1, 0)) )
    index += 4

    # Write "Hello" to Terminal area
    mem.setData(index, genInstruction(0x05, genReg(0, -1, ord('H'))) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8010) )
    index += 4
    mem.setData(index, genInstruction(0x05, genReg(0, -1, ord('e'))) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8011) )
    index += 4
    mem.setData(index, genInstruction(0x05, genReg(0, -1, ord('l'))) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8012) )
    index += 4
    mem.setData(index, genInstruction(0x05, genReg(0, -1, ord('l'))) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8013) )
    index += 4
    mem.setData(index, genInstruction(0x05, genReg(0, -1, ord('o'))) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8014) )
    index += 4
    # Resize, set new height 3 lines
    mem.setData(index, genInstruction(0x06, 0x03BB) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8000) )
    index += 4
    # Print terminal
    mem.setData(index, genInstruction(0x05, genReg(0, -1, 0x01)) )
    index += 4
    mem.setData(index, genInstruction(0x02, 0x8000) )
    index += 4

    mem.setData(index, genInstruction(0xFF, 0) )
    index += 4


def main():
    # 10k
    mainmem = Mem(1024*10)
    term = Terminal()
    term.setBase(0x8010)
    mainmem.addSpecial(0x8000, None, term.setControl)
    mainmem.addSpecial(0x8001, None, term.setControl)
    mainmem.addSpecial(0x8002, None, term.setControl)
    mainmem.addSpecial(0x8003, None, term.setControl)
    for i in xrange(100):
        mainmem.addSpecial(0x8010 + i, term.getData, term.setData)
    program(mainmem)

    cpu = RISC1(mainmem, ALU())
    cpu.start()

if __name__ == "__main__":
    main()
