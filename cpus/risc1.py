from opcodes import Opcodes
from primitives import IntVec
from primitives import Stack
from primitives import MMU
import time

class RISC1:
    wordsize = 4

    def __init__(self, code, mem, alu):
        self.code = code
        self.mem = mem
        self.mmu = MMU(mem)
        self.alu = alu
        self.regs = {}
        #self.intvec = None
        self.opcodes = Opcodes()
        self.cycle = 0
        self.interrupt = []
        self.inthandler = None
        for num in xrange(255):
            self.regs['r%s' % (num)] = 0

        # This is register containing Program Counter
        self.pc = 'r42'
        # Stack register
        self.stackreg = 'r43'
        # Return register
        self.retreg = 'r44'
        self.intvec = IntVec()
        self.intvec.read(self.code, 0, self.wordsize)

    def fetch(self):
        self.cycle += 1
        inst = self.code.getData(self.regs[self.pc], self.wordsize)
        self.regs[self.pc] += self.wordsize
        return inst

    def decode(self, inst):
        self.cycle += 1
        opcode = inst & 0xFF
        imm = (inst >> 8)
        return (opcode, imm)

    def load(self, imm, size=None):
        if size is None:
            size = self.wordsize
        return self.mmu.getData(imm, size)

    def store(self, imm, data, size=None):
        if size is None:
            size = self.wordsize
        self.mmu.setData(imm, data, size)

    def solveRegs(self, datas):
        x = datas & 0xff
        y = (datas >> 8) & 0xFF
        i = (datas >> 16) & 0xFF
        return (x, y, i)

    def solveRegNames(self, datas):
        (x, y, i) = self.solveRegs(datas)
        rx = None
        ry = None
        imm = None
        if x > 0:
            rx = 'r%s' % (x - 1)
        if y > 0:
            ry = 'r%s' % (y - 1)
        if i > 0:
            imm = i

        return (rx, ry, imm)

    def solveValues(self, datas):
        (rx, ry, imm) = self.solveRegNames(datas)
        xval = 0
        yval = 0
        immval = 0
        if rx is not None:
            xval = self.regs[rx]
        if ry is not None:
            yval = self.regs[ry]
        if imm is not None:
            immval = imm

        return (xval, yval, immval)

    def dump(self):
        print ("PC: %s" % (self.regs[self.pc]))
        for num in xrange(255):
            val = self.regs['r%s' % (num)]
            if val != 0:
                print ("%4s: %.8x" % ('r%x' % num, val))

    def handleLoadStoreXBits(self, loadorstore, imm, size):
        (rx, ry, imm) = self.solveRegNames(imm)
        rimm = 0

        if loadorstore == 'load':
            if ry is not None:
                rimm = self.regs[ry]
            #if size == 8:
            #    self.regs[rx] = self.load(rimm, 4)
            #    self.regs[ry] = self.load(rimm + 4, 4)
            #else:
            self.regs[rx] = self.load(rimm, size)
        elif loadorstore == 'store':
            if ry is None:
                ry = 'r0'
            if rx is not None:
                rimm = self.regs[rx]
            #if size == 8:
            #    self.store(rimm, self.regs[ry], 4)
            #    self.store(rimm + 4, self.regs['r0'], 4)
            #else:
            self.store(rimm, self.regs[ry], size)

    def handleLoad(self, imm, size):
        self.handleLoadStoreXBits('load', imm, size)

    def handleStore(self, imm, size):
        self.handleLoadStoreXBits('store', imm, size)

    def handleStoreLoad(self, op, imm):
        handled = False
        if op == self.opcodes.rev_opcodes['LOAD8i']:
            self.regs['r0'] = self.load(imm, 1)
            handled = True
        elif op == self.opcodes.rev_opcodes['LOAD16i']:
            self.regs['r0'] = self.load(imm, 2)
            handled = True
        elif op == self.opcodes.rev_opcodes['LOAD32i']:
            self.regs['r0'] = self.load(imm, 4)
            handled = True
        elif op == self.opcodes.rev_opcodes['STORE8i']:
            self.store(imm, self.regs['r0'], 1)
            handled = True
        elif op == self.opcodes.rev_opcodes['STORE16i']:
            self.store(imm, self.regs['r0'], 2)
            handled = True
        elif op == self.opcodes.rev_opcodes['STORE32i']:
            self.store(imm, self.regs['r0'], 4)
            handled = True
        elif op == self.opcodes.rev_opcodes['LOAD8']:
            self.handleLoad(imm, 1)
            handled = True
        elif op == self.opcodes.rev_opcodes['LOAD16']:
            self.handleLoad(imm, 2)
            handled = True
        elif op == self.opcodes.rev_opcodes['LOAD32']:
            self.handleLoad(imm, 4)
            handled = True
        #elif op == self.opcodes.rev_opcodes['LOAD64']:
        #    self.handleLoad(imm, 8)
        #    handled = True
        elif op == self.opcodes.rev_opcodes['STORE8']:
            self.handleStore(imm, 1)
            handled = True
        elif op == self.opcodes.rev_opcodes['STORE16']:
            self.handleStore(imm, 2)
            handled = True
        elif op == self.opcodes.rev_opcodes['STORE32']:
            self.handleStore(imm, 4)
            handled = True
        #elif op == self.opcodes.rev_opcodes['STORE64']:
        #    self.handleStore(imm, 8)
        #    handled = True
        elif op == self.opcodes.rev_opcodes['LOADADDRi']:
            self.regs['r0'] = imm
            handled = True

        if handled:
            self.cycle += 3

        return handled

    def handleMov(self, op, imm):
        handled = False
        if op == self.opcodes.rev_opcodes['MOV']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None:
                src = 0            
                if ry is not None:
                    src = self.regs[ry]
                if imm is not None:
                    src += imm
                self.regs[rx] = src
                handled = True
        elif op == self.opcodes.rev_opcodes['MOVi']:
            self.regs['r0'] = imm
            handled = True
        elif op == self.opcodes.rev_opcodes['SWP']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if imm is None:
                imm = 0
            if rx is not None and ry is not None:
                tmp = self.regs[rx]
                self.regs[rx] = self.regs[ry] + imm
                self.regs[ry] = tmp + imm
                handled = True

        if handled:
            self.cycle += 2
        return handled

    def handleBasicALU(self, op, imm):
        handled = False
        if op == self.opcodes.rev_opcodes['ADD']:
            (rx, ry, dum) = self.solveRegNames(imm)
            if rx is not None:
                self.regs[rx] = self.alu.add(*self.solveValues(imm))
            handled = True
        elif op == self.opcodes.rev_opcodes['SUB']:
            (rx, ry, dum) = self.solveRegNames(imm)
            if rx is not None:
                self.regs[rx] = self.alu.sub(*self.solveValues(imm))
            handled = True
        elif op == self.opcodes.rev_opcodes['MUL']:
            (rx, ry, dum) = self.solveRegNames(imm)
            if rx is not None:
                self.regs[rx] = self.alu.mul(*self.solveValues(imm))
            handled = True
        elif op == self.opcodes.rev_opcodes['DIV']:
            (rx, ry, dum) = self.solveRegNames(imm)
            if rx is not None:
                self.regs[rx] = self.alu.div(*self.solveValues(imm))
            handled = True
        elif op == self.opcodes.rev_opcodes['MOD']:
            (rx, ry, dum) = self.solveRegNames(imm)
            if rx is not None:
                self.regs[rx] = self.alu.mod(*self.solveValues(imm))
            handled = True

        if handled:
            self.cycle += 1
        return handled

    def handleBitwiseALU(self, op, imm):
        handled = False
        if op == self.opcodes.rev_opcodes['SHL']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and imm is not None:
                if ry is not None:
                    target = ry
                else:
                    target = rx
                self.regs[target] = self.alu.b_shl(self.regs[rx], imm)
                handled = True
        elif op == self.opcodes.rev_opcodes['SHR']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and imm is not None:
                if ry is not None:
                    target = ry
                else:
                    target = rx
                self.regs[target] = self.alu.b_shr(self.regs[rx], imm)
                handled = True
        elif op == self.opcodes.rev_opcodes['AND']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and ry is not None:
                self.regs[rx] = self.alu.b_and(self.regs[rx], self.regs[ry])
                handled = True
        elif op == self.opcodes.rev_opcodes['OR']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and ry is not None:
                self.regs[rx] = self.alu.b_or(self.regs[rx], self.regs[ry])
                handled = True
        elif op == self.opcodes.rev_opcodes['XOR']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and ry is not None:
                self.regs[rx] = self.alu.b_xor(self.regs[rx], self.regs[ry])
                handled = True
        elif op == self.opcodes.rev_opcodes['NOT']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None:
                if ry is not None:
                    target = ry
                else:
                    target = rx
                self.regs[target] = self.alu.b_not(rx)
                handled = True

        if handled:
            self.cycle += 1

        return handled

    def handleBranching(self, op, imm):
        handled = False

        if op == self.opcodes.rev_opcodes['Bi']:
            self.regs[self.pc] = imm
            handled = True
        elif op == self.opcodes.rev_opcodes['B']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None:
                self.regs[self.pc] = self.regs[rx]
            handled = True
        elif op == self.opcodes.rev_opcodes['BZi']:
            if self.regs['r0'] == 0:
                self.regs[self.pc] = imm
            handled = True
        elif op == self.opcodes.rev_opcodes['BZ']:
            (rx, ry, imm) = self.solveRegNames(imm)
            reg = 'r0'
            if ry is not None:
                reg = ry
            if self.regs[reg] == 0:
                self.regs[self.pc] = self.regs[rx]
            handled = True
        elif op == self.opcodes.rev_opcodes['BNZi']:
            if self.regs['r0'] != 0:
                self.regs[self.pc] = imm
            handled = True
        elif op == self.opcodes.rev_opcodes['BNZ']:
            (rx, ry, imm) = self.solveRegNames(imm)
            reg = 'r0'
            if ry is not None:
                reg = ry
            if self.regs[reg] != 0:
                self.regs[self.pc] = self.regs[rx]
            handled = True
        elif op == self.opcodes.rev_opcodes['BE']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and ry is not None and imm is not None:
                if self.regs[rx] == self.regs[ry]:
                    self.regs[self.pc] += imm
                handled = True
        elif op == self.opcodes.rev_opcodes['BNE']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and ry is not None and imm is not None:
                if self.regs[rx] != self.regs[ry]:
                    self.regs[self.pc] += imm
                handled = True
        elif op == self.opcodes.rev_opcodes['BLE']:
            (rx, ry, imm) = self.solveRegNames(imm)
            im = 0
            if imm is not None:
                im = imm
            if rx is not None and ry is not None:
                if self.regs[ry] == 0:
                    self.regs[self.pc] = self.regs[rx] + im
                handled = True
        elif op == self.opcodes.rev_opcodes['BSUBi']:
            self.regs[self.retreg] = self.pc + self.wordsize
            self.regs[self.pc] = imm
        elif op == self.opcodes.rev_opcodes['BSUB']:
            self.regs[self.retreg] = self.pc + self.wordsize
            (rx, ry, imm) = self.solveRegNames(imm)
            if imm is None:
                imm = 0
            if rx is not None:
                imm += self.regs[rx]
            self.regs[self.pc] = imm
        elif op == self.opcodes.rev_opcodes['BRET']:
            self.regs[self.pc] = self.regs[self.retreg]

        if handled:
            self.cycle += 5

        return handled

    def illegalInstruction(self, op, imm):
        raise ValueError('Illegal instruction: %s  (%s)' % (op, imm))

    def handleIntvec(self, op, imm):
        """ Check if we have intvec opcode.
            If found, try to read and setup new Iterrupt Vector or setup new flags.
        """
        handled = False
        if op == self.opcodes.rev_opcodes['INTVEC']:
            (rx, ry, imm) = self.solveRegNames(imm)

            if rx is not None:
                pos = self.regs[rx]
                if imm is not None:
                    pos += imm
                self.intvec = IntVec()
                self.intvec.read(self.mmu, pos, self.wordsize)
                handled = True

            if ry is not None and self.intvec is not None:
                flags = self.regs[ry]
                self.intvec.setFlags(flags)
                handled = True
        elif op == self.opcodes.rev_opcodes['SETI']:
            self.intvec.setFlags(1)
            handled = True
        elif op == self.opcodes.rev_opcodes['CLRI']:
            self.intvec.setFlags(0)
            handled = True

        return handled

    def handleMMU(self, op, imm):
        """ Check if we have intvec opcode.
            If found, try to read and setup new Iterrupt Vector or setup new flags.
        """
        handled = False
        if op == self.opcodes.rev_opcodes['MAP']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is not None and ry is not None:
                pos = self.regs[rx]
                size = self.regs[ry]
                self.mmu.initialize(pos, size)
            if imm is not None:
                if imm & 0x1 == 0x1:
                    self.mmu.enable()
                if imm & 0x2 == 0x2:
                    self.mmu.disable()
            handled = True

        return handled

    def handleStack(self, op, imm):
        handled = False
        if op == self.opcodes.rev_opcodes['PUSH']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is None:
                dest = self.stackreg
            else:
                dest = rx

            if ry is None:
                data = 0
            else:
                data = self.regs[ry]

            if imm is None:
                imm = 0
            data += imm

            stack = Stack(self.regs[dest], self.mmu, self.wordsize)
            stack.push(data)
            self.regs[dest] = stack.getPos()
            del stack

            handled = True
        elif op == self.opcodes.rev_opcodes['POP']:
            (rx, ry, imm) = self.solveRegNames(imm)
            if rx is None:
                dest = self.stackreg
            else:
                dest = rx

            if imm is None:
                imm = 0

            stack = Stack(self.regs[dest], self.mmu, self.wordsize)
            data = stack.pop()
            self.regs[dest] = stack.getPos()
            del stack

            if ry is not None:
                self.regs[ry] = data + imm

            handled = True

        return handled

    def saveState(self):
        tmp = {}
        tmp['pc'] = self.regs[self.pc]
        tmp['stack'] = self.regs[self.stackreg]
        tmp['regs'] = self.regs.copy()
        return tmp

    def loadState(self, state):
        self.regs = tmp['regs']
        self.regs[self.pc] = tmp['pc']
        self.regs[self.stackreg] = tmp['stack']

    def raiseInterrupt(self, intnum):
        if self.intvec is None:
            return
    
        if not self.intvec.isEnabled():
            return

        self.intvec.disable()
        self.interrupt.append(intnum)
        #print "int", self.interrupt

    def handleInterrupts(self):
        if not self.interrupt:
            return

        intnum = self.interrupt[0]
        self.interrupt = self.interrupt[1:]

        handler = self.intvec.getHandler(intnum)
        if handler is not None:
            #mystate = self.saveState()

            self.regs[self.retreg] = self.regs[self.pc]

            self.regs[self.pc] = handler
            #self.loadState(mystate)

    def returnInterrupt(self):
        self.regs[self.pc] = self.regs[self.retreg]

        self.intvec.enable()

    def start(self, verbose=False):
    #def start(self, verbose=True):
        while True:
            if self.interrupt is not None:
                self.handleInterrupts()

            inst = self.fetch()
            (op, imm) = self.decode(inst)
            if verbose:
                if (op in self.opcodes.opcodes and self.opcodes.opcodes[op][-1] == 'i'):
                    print ("[PC %4s] %3s %s %s" % (self.regs[self.pc], op, self.opcodes.opcodes[op], imm))
                else:
                    print ("[PC %4s] %3s %s %s" % (self.regs[self.pc], op, self.opcodes.opcodes[op], self.solveRegNames(imm)))

            if op == self.opcodes.rev_opcodes['STOP']:
                break

            handled = False

            # Are we returning from an interrupt?
            if op == self.opcodes.rev_opcodes['IRET']:
                self.returnInterrupt()
                handled = True

            ## Store/Load
            if not handled:
                handled = self.handleStoreLoad(op, imm)

            ## MOV/SWP
            if not handled:
                handled = self.handleMov(op, imm)

            ## ALU
            if not handled:
                handled = self.handleBasicALU(op, imm)
            if not handled:
                handled = self.handleBitwiseALU(op, imm)

            ## Branching
            if not handled:
                handled = self.handleBranching(op, imm)

            # Interrupt vector
            if not handled:
                handled = self.handleIntvec(op, imm)

            # Stack
            if not handled:
                self.handleStack(op, imm)

            # MMU / Mapping
            if not handled:
                handled = self.handleMMU(op, imm)

            if not handled:
                self.illegalInstruction(op, imm)

        self.dump()

""" Instruction set - 32 bit

imm         coding = AABBCC
rx          coding = 0000xx
rx, ry      coding = 00yyxx
rx, ry, imm coding = iiyyxx

0x00 NOP
0x01 LOAD8i imm
  Load 8 bit value from imm memory location to r0
0x02 LOAD16i imm
  Load 16 bit value from imm memory location to r0
0x03 LOAD32i imm
  Load 32 bit value from imm memory location to r0
0x04 STORE8i imm
  Store 8 bit value from r0 to memory location imm
0x05 STORE16i imm
  Store 16 bit value from r0 to memory location imm
0x06 STORE32i imm
  Store 32 bit value from r0 to memory location imm
0x07 LOAD8 rx, ry
  Load 8 bit value from ry memory location to rx/r0
0x08 LOAD16 rx, ry
  Load 16 bit value from ry memory location to rx/r0
0x09 LOAD32 rx, ry
  Load 32 bit value from ry memory location to rx/r0
#0x0A LOAD64 rx, ry
#  Load 64 bit value from ry memory location to rx/r0 = low 32 bit, ry = high 32 bit
0x0B STORE8 rx, ry
  Store 8 bit value to rx memory location from ry/r0
0x0C STORE16 rx, ry
  Store 16 bit value to rx memory location from ry/r0
0x0D STORE32 rx, ry
  Store 32 bit value to rx memory location from ry/r0
#0x0E STORE64 rx, ry, imm
#  Store 64 bit value to rx memory location from ry/r0 = low 32 bit, r0 = high 32 bit
0x0F LOADADDR imm
  Load address of immediate to r0

0x10 ADD rx, ry, imm
  Do rx = rx + ry + imm, store result to rx
0x11 SUB rx, ry, imm
  Subtract rx = rx - ry - imm, store result to rx
0x12 MUL rx, ry, imm
  Multiply rx = rx * ry * imm, store result to rx
0x13 DIV rx, ry, imm
  Divide rx = rx / ry /imm, store result to rx
0x14 MOD rx, ry, imm
  Take remainder of rx = rx % ry % imm, store result to rx
0x15 SHL rx, ry, imm
  Shift left rx by imm, store result to ry or in rx if ry not defined
0x16 SHR rx, ry, imm
  Shift right rx by imm, store result to ry or in rx if ry not defined
0x17 AND rx, ry
  Does bitwise and (rx&ry), store result to rx
0x18 OR rx, ry
  Does bitwise or (rx|ry), store result to rx
0x19 XOR rx, ry
  Does bitwise exclusive or (rx^ry), store result to rx
0x20 NOT rx
  Does bitwise not (~rx), store result to ry or rx if ry not defined

0x21 PUSH rx, ry, imm
  Push value of ry+imm to stack defined in rx or in case rx==0 use r43
0x22 POP rx, ry, imm
  Pop value+imm to register ry from stack defined in rx or in case rx==0 use r43
0x23 MOV rx, ry, imm
  Move value of register ry to register rx, add imm
0x24 MOVi imm
  Move imm to r0
0x25 SWP rx, ry, imm
  Swap value of registers ry and rx, add imm to both

0x2D MAP rx, ry, imm
  Define MMU page map table
   rx = physical address for page start, can't be zero. If zero, just read immediate
   ry = number of items in table
   imm = 0x0 = no change, 0x1 enable paging, 0x2 disable paging
  Table should contain mapping items like:
    0x00006100 # Page, virtual start at 24, size 4k (0x1000)
    0x00001101 # Subtable, starts at phys 4k (0x1000)
    0x00008110 # Page, virtual start at 32k, size 64k (0x10000)
    0x00018100 # Page, virtual start at 96, size 4k (0x1000)
  Format is:
    0xFFFFF000 == address, virtual in case of page, physical in case of subtable
    0x???????1 == subtable,  0=page,              1=subtable
    0x???????2 == execute,   0=no execute,        1=executable
    0x???????4 == write,     0=no write,          1=writable
    0x???????8 == userspace, 0=no access from us, 1=accessable
    0x?????1?? == ok,        0=disabled,          1=in use
    0x??????0? == 4k page
    0x??????1? == 64k page
    0x??????2? == 1M page
    0x??????3? == 64M page
            if flags & 0x1 == 0x1:
                data['subtable'] = True
            if flags & 0x2 == 0x2:
                data['execute'] = True
            if flags & 0x4 == 0x4:
                data['write'] = True
            if flags & 0x8 == 0x8:
                data['userspace'] = True
            if flags & 0x10 == 0x10:
                data['size1'] = True
            if flags & 0x20 == 0x20:
                data['size2'] = True
            if flags & 0x100 == 0x100:
                data['ok'] = True
  
0x2E START rx, ry, imm
  Start a HW process
   rx + imm = Address of first instruction
   ry = Address of process structure (see Appendix A)
0x2F INTVEC rx, ry, imm
  Program interrupt vector, by default read from position 0
   rx + imm = Address of interrupt vector or 0 == no change
   ry = Interrupt flags (enable/disable/etc)

0x30 Bi imm
  Branch to location imm
0x31 B rx
  Branch to location defined by rx
0x32 BZi imm
  Branch to location imm, if r0 is zero
0x33 BZ rx, ry
  Branch to location defined by rx, if ry/r0 is zero
0x34 BNZi imm
  Branch to location imm, if r0 is not zero
0x35 BNZ rx, ry
  Branch to location defined by rx, if ry/r0 is not zero
0x36 BE rx, ry, imm
  Increase PC by imm if value rx == ry
0x37 BNE rx, ry, imm
  Increase PC by imm if value rx != ry
0x38 BLE rx, ry, imm
  Branch long if ry is zero, target address = rx + imm
0x3A BSUBi imm
  Branch to subprocess defined by imm, save return address to return register
0x3B BSUB rx, ry, imm
  Branch to subprocess, save return address to return register
    rx + imm = subprocess address
0x3C BRET
  Return from a subprocess
0x3D IRET
  Return from an interrupt
0x3E SETI
  Turn interrupts on
0x3F CLRI
  Turn interrupts off

0x40 CO rx, ry, imm
  Co-processor query call, will write:
    rx = Return status register for information about coprocessors
    ry = Return status register for reference number for communication
0x41 COS rx, ry, imm
  Order a co-processor to start running code
    rx = beginning of code to run
    ry = refernce nuber for communication
    imm = index of co-processor
0x42 COQ rx, ry, imm
  Query status of co-processor
    rx = Return status register of co-processor
    ry = refernce nuber for communication
    imm = index of co-processor
0x43 COH rx, ry, imm
  Halt co-processor
    rx = Free form data to pass to co-processor
    ry = refernce nuber for communication
    imm = index of co-processor

0xFF END
  End execution

Appendix A - HW process table
 HW task/process structure
 pid       Process ID. Shoulb be 0, will be changed by START opcode
 perm      permissions flags
 PC        program counter
 r0..r255  registers
"""
