#!/usr/bin/env python

import sys

from primitives import CPUMem
from primitives import ALU
from cpus import RISC1

def genInstruction(inst, imm):
    inst = inst & 0xFF
    imm = imm & 0xFFFFFF
    imm <<= 8
    return (inst | imm)

def genReg(x,y,i):
    x = x & 0xFF
    y = (y & 0xFF) << 8
    i = (i & 0xFF) << 16
    return (x | y | i)
        
def program(mem):
    index = 0

    mem.setRaw(index, genInstruction(0x01, 100) )
    mem.setRaw(100, 10)
    index +=1
    mem.setRaw(index, genInstruction(0x10, genReg(0,0,5)) )
    index +=1
    mem.setRaw(index, genInstruction(0xFF, 0) )
    index +=1


def main():
    # 10k
    mainmem = CPUMem(1024*10)
    program(mainmem)

    cpu = RISC1(mainmem, ALU())
    cpu.start()

if __name__ == "__main__":
    main()
