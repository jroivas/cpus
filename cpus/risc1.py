from opcodes import Opcodes

class RISC1:
    wordsize = 4

    def __init__(self, mem, alu):
        self.mem = mem
        self.alu = alu
        self.pc = 0
        self.regs = {}
        self.opcodes = Opcodes()
        for num in xrange(255):
            self.regs['r%s' % (num)] = 0

    def fetch(self):
        inst = self.mem.getData(self.pc, self.wordsize)
        self.pc += self.wordsize
        return inst

    def decode(self, inst):
        opcode = inst & 0xFF
        imm = (inst >> 8)
        return (opcode, imm)

    def load(self, imm):
        return self.mem.getData(imm, self.wordsize)

    def store(self, imm, data):
        self.mem.setData(imm, data)

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
        """
        if rx is not None:
            xval = self.regs['r%s' % xval]
        if ry is not None:
            yval = self.regs['r%s' % yval]
        """
        if imm is not None:
            immval = imm

        return (xval, yval, immval)

    def dump(self):
        print ("PC: %s" % (self.pc))
        for num in xrange(255):
            val = self.regs['r%s' % (num)]
            if val != 0:
                print ("r%x: %s" % (num, val))

    def start(self):
        while True:
            inst = self.fetch()
            (op, imm) = self.decode(inst)
            if (op in self.opcodes.opcodes and self.opcodes.opcodes[op][-1] == 'i') or op == self.opcodes.rev_opcodes['B']:
                print ("[PC %s] %s %s" % (self.pc, op, imm))
            else:
                print ("[PC %s] %s %s" % (self.pc, op, self.solveRegNames(imm)))
            if op == self.opcodes.rev_opcodes['STOP']:
                break
            elif op == self.opcodes.rev_opcodes['LOADi']:
                self.regs['r0'] = self.load(imm)
            elif op == self.opcodes.rev_opcodes['STOREi']:
                 self.store(imm, self.regs['r0'])
            elif op == self.opcodes.rev_opcodes['LOAD']:
                (rx, ry, imm) = self.solveRegNames(imm)
                rimm = 0
                if rx is not None:
                    rimm = self.regs[rx]
                if imm is not None:
                    rimm += imm
                if ry is None:
                    ry = 'r0'
                self.regs[ry] = self.load(rimm)
            elif op == self.opcodes.rev_opcodes['STORE']:
                (rx, ry, imm) = self.solveRegNames(imm)
                rimm = 0
                if rx is not None:
                    rimm = self.regs[rx]
                if imm is not None:
                    rimm += imm
                if ry is None:
                    ry = 'r0'
                self.store(rimm, self.regs[ry])
            elif op == self.opcodes.rev_opcodes['MOV']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None:
                    src = 0            
                    if ry is not None:
                        src = self.regs[ry]
                    if imm is not None:
                        src += imm
                    self.regs[rx] = src
            elif op == self.opcodes.rev_opcodes['MOVi']:
                self.regs['r0'] = imm
            elif op == self.opcodes.rev_opcodes['SWP']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if imm is None:
                    imm = 0
                if rx is not None and ry is not None:
                    tmp = self.regs[rx]
                    self.regs[rx] = self.regs[ry] + imm
                    self.regs[ry] = tmp + imm
            elif op == self.opcodes.rev_opcodes['ADD']:
                self.regs['r0'] += self.alu.add(*self.solveValues(imm))
            elif op == self.opcodes.rev_opcodes['SUB']:
                self.regs['r0'] += self.alu.sub(*self.solveValues(imm))
            elif op == self.opcodes.rev_opcodes['MUL']:
                self.regs['r0'] += self.alu.mul(*self.solveValues(imm))
            elif op == self.opcodes.rev_opcodes['DIV']:
                self.regs['r0'] += self.alu.div(*self.solveValues(imm))
            elif op == self.opcodes.rev_opcodes['MOD']:
                self.regs['r0'] += self.alu.mod(*self.solveValues(imm))
            elif op == self.opcodes.rev_opcodes['SHL']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and imm is not None:
                    if ry is not None:
                        target = ry
                    else:
                        target = rx
                    self.regs[target] = self.alu.b_shl(self.regs[rx], imm)
            elif op == self.opcodes.rev_opcodes['SHR']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and imm is not None:
                    if ry is not None:
                        target = ry
                    else:
                        target = rx
                    self.regs[target] = self.alu.b_shr(self.regs[rx], imm)
            elif op == self.opcodes.rev_opcodes['AND']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and ry is not None:
                    self.regs['r0'] = self.alu.b_and(self.regs[rx], self.regs[ry])
            elif op == self.opcodes.rev_opcodes['OR']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and ry is not None:
                    self.regs['r0'] = self.alu.b_or(self.regs[rx], self.regs[ry])
            elif op == self.opcodes.rev_opcodes['XOR']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and ry is not None:
                    self.regs['r0'] = self.alu.b_xor(self.regs[rx], self.regs[ry])
            elif op == self.opcodes.rev_opcodes['NOT']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None:
                    if ry is not None:
                        target = ry
                    else:
                        target = rx
                    self.regs[target] = self.alu.b_not(rx)
            ## Branching
            elif op == self.opcodes.rev_opcodes['B']:
                print "Brancing from %s" % (self.pc)
                self.pc = imm
                print "Brancing to %s" % (imm)
            elif op == self.opcodes.rev_opcodes['BZ']:
                if self.regs['r0'] == 0:
                    self.pc = imm
            elif op == self.opcodes.rev_opcodes['BNZ']:
                if self.regs['r0'] != 0:
                    self.pc = imm
            elif op == self.opcodes.rev_opcodes['BE']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and ry is not None and imm is not None:
                    if self.regs[rx] == self.regs[ry]:
                        self.pc += imm
            elif op == self.opcodes.rev_opcodes['BNE']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None and ry is not None and imm is not None:
                    if self.regs[rx] != self.regs[ry]:
                        self.pc += imm
            elif op == self.opcodes.rev_opcodes['BLE']:
                (rx, ry, imm) = self.solveRegNames(imm)
                im = 0
                if imm is not None:
                    im = imm
                if rx is not None and ry is not None:
                    if self.regs[ry] == 0:
                        self.pc = self.regs[rx] + im
        self.dump()

""" Instruction set

imm         coding = AABBCC
rx          coding = 0000xx
rx, ry      coding = 00yyxx
rx, ry, imm coding = iiyyxx

0x00 NOP
0x01 LOAD imm
  Load value from imm memory location to r0
0x02 STORE imm
  Store value to imm memory location from r0
0x03 LOAD rx, ry, imm
  Load value from (rx+imm) memory location to ry/r0
0x04 STORE rx, ry, imm
  Store value to (rx+imm) memory location from ry/r0
0x05 MOV rx, ry, imm
  Move value of register ry to register rx, add imm
0x06 MOVi imm
  Move imm to r0
0x07 SWP rx, ry, imm
  Swap value of registers ry and rx, add imm to both

0x10 ADD rx, ry, imm
  Add rx + ry + imm, store result to r0
0x11 SUB rx, ry, imm
  Subtract rx - ry - imm, store result to r0
0x12 MUL rx, ry, imm
  Multiply rx * ry * imm, store result to r0
0x13 DIV rx, ry, imm
  Divide rx / ry /imm, store result to r0
0x14 MOD rx, ry, imm
  Take remainder of  rx % ry % imm, store result to r0
0x15 SHL rx, ry, imm
  Shift left rx by imm, store result to ry or in rx if ry not defined
0x16 SHR rx, ry, imm
  Shift right rx by imm, store result to ry or in rx if ry not defined
0x17 AND rx, ry
  Does bitwise and (rx&ry), store result to r0
0x18 OR rx, ry
  Does bitwise or (rx|ry), store result to r0
0x19 XOR rx, ry
  Does bitwise exclusive or (rx^ry), store result to r0
0x20 NOT rx
  Does bitwise not (~rx), store result to ry or rx if ry not defined


0x30 B imm
  Branch to location imm
0x31 BZ imm
  Branch to location imm, if r0 is zero
0x32 BNZ imm
  Branch to location imm, if r0 is not zero
0x33 BE rx, ry, imm
  Increase PC by imm if value rx == ry
0x34 BNE rx, ry, imm
  Increase PC by imm if value rx != ry
0x35 BLE rx, ry, imm
  Branch long if ry is zero, target address = rx + imm

0xFF END
  End execution
"""
