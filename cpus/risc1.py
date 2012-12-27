class RISC1:
    opcodes = {
        0x00: 'NOP',
        0x01: 'LOADi',
        0x02: 'STOREi',
        0x03: 'LOAD',
        0x04: 'STORE',
        0x05: 'MOV',
        0x06: 'MOVi',
        0x07: 'SWP',
        0x10: 'ADD',
        0x11: 'SUB',
        0xFF: 'STOP'
        }
    wordsize = 4

    def __init__(self, mem, alu):
        self.mem = mem
        self.alu = alu
        self.pc = 0
        self.regs = {}
        for num in xrange(255):
            self.regs['r%s' % (num)] = 0
        self.rev_opcodes = {v:k for k, v in self.opcodes.iteritems()}

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
        (x,y,i) = self.solveRegs(datas)
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
            xval = self.regs['r%s' % xval]
        if ry is not None:
            yval = self.regs['r%s' % yval]
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
            if op in self.opcodes and self.opcodes[op][-1] == 'i':
                print ("[PC %s] %s %s" % (self.pc, op, imm))
            else:
                print ("[PC %s] %s %s" % (self.pc, op, self.solveRegNames(imm)))
            if op == self.rev_opcodes['STOP']:
                break
            elif op == self.rev_opcodes['LOADi']:
                self.regs['r0'] = self.load(imm)
            elif op == self.rev_opcodes['STOREi']:
                 self.store(imm, self.regs['r0'])
            elif op == self.rev_opcodes['LOAD']:
                (rx, ry, imm) = self.solveRegNames(imm)
                rimm = 0
                if rx is not None:
                    rimm = self.regs[rx]
                if imm is not None:
                    rimm += imm
                if ry is None:
                    ry = 'r0'
                self.regs[ry] = self.load(rimm)
            elif op == self.rev_opcodes['STORE']:
                (rx, ry, imm) = self.solveRegNames(imm)
                rimm = 0
                if rx is not None:
                    rimm = self.regs[rx]
                if imm is not None:
                    rimm += imm
                if ry is None:
                    ry = 'r0'
                self.store(rimm, self.regs[ry])
            elif op == self.rev_opcodes['MOV']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None:
                    src = 0            
                    if ry is not None:
                        src = self.regs[ry]
                    if imm is not None:
                        src += imm
                    self.regs[rx] = src
            elif op == self.rev_opcodes['MOVi']:
                self.regs['r0'] = imm
            elif op == self.rev_opcodes['SWP']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if imm is None:
                    imm = 0
                if rx is not None and ry is not None:
                    tmp = self.regs[rx]
                    self.regs[rx] = self.regs[ry] + imm
                    self.regs[ry] = tmp + imm
            elif op == self.rev_opcodes['ADD']:
                self.regs['r0'] += self.alu.add(*self.solveValues(imm))
        self.dump()

""" Instruction set

IMM         coding = AABBCC
rx          coding = 0000xx
rx, ry      coding = 00yyxx
rx, ry, imm coding = iiyyxx

0x00 NOP
0x01 LOAD IMM
  Load value from IMM memory location to r0
0x02 STORE IMM
  Store value to IMM memory location from r0
0x03 LOAD rx, ry, imm
  Load value from (rx+imm) memory location to ry/r0
0x04 STORE rx, ry, imm
  Store value to (rx+imm) memory location from ry/r0
0x05 MOV rx, ry, imm
  Move value of register ry to register rx, add imm
0x06 MOVi IMM
  Move IMM to r0
0x07 SWP rx, ry, imm
  Swap value of registers ry and rx, add imm to both

0x10 ADD rx, ry, imm
0x11 SUB rx, ry, imm
0x12 MUL rx, ry, imm
0x13 DIV rx, ry, imm
0x14 MOD rx, ry, imm
0x15 SHL rx, ry, imm
0x16 SHR rx, ry, imm
0x17 AND rx, ry, imm
0x18 OR rx, ry
0x19 XOR rx, ry
0x20 NOT rx
0xFF END
  End execution
"""
