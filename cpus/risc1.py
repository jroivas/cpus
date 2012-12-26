class RISC1:
    opcodes = {
        0x00: 'NOP',
        0x01: 'LOADi',
        0x02: 'STOREi',
        0x03: 'LOAD',
        0x04: 'STORE',
        0x05: 'MOV',
        0x10: 'ADD',
        0x11: 'SUB',
        0xFF: 'STOP'
        }

    def __init__(self, mem, alu):
        self.mem = mem
        self.alu = alu
        self.pc = 0
        self.regs = {}
        #self.reg_names = ['r0','r1','r2','r3','r4']
        #for name in self.reg_names:
        for num in xrange(255):
            self.regs['r%s' % (num)] = 0
        self.rev_opcodes = {}
        self.rev_opcodes = {v:k for k, v in self.opcodes.iteritems()}
        #for key, val in self.opcodes.iteritems():
        #    self.rev_opcodes[val] = key

    def fetch(self):
        inst = self.mem.getRaw(self.pc)
        self.pc += 1
        return inst

    def decode(self, inst):
        opcode = inst & 0xFF
        imm = (inst >> 8)
        return (opcode, imm)

    def load(self, imm):
        return self.mem.getRaw(imm)

    def store(self, imm, data):
        self.mem.setRaw(imm, data)

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
            #print ("[PC %s] %s %s" % (self.pc, op, imm))
            if op == self.rev_opcodes['STOP']:
                break
            elif op == self.rev_opcodes['LOADi']:
                self.regs['r0'] = self.load(imm)
            elif op == self.rev_opcodes['STOREi']:
                 self.store(imm, self.regs['r0'])
            elif op == self.rev_opcodes['MOV']:
                (rx, ry, imm) = self.solveRegNames(imm)
                if rx is not None:
                    src = 0            
                    if ry is not None:
                        src = self.regs[ry]
                    if imm is not None:
                        src += imm
                    self.regs[rx] = src
            elif op == self.rev_opcodes['ADD']:
                self.regs['r0'] += self.alu.add(*self.solveValues(imm))
        self.dump()

""" Instruction set

IMM         coding = AABBCC
rx          coding = 0000xx
rx, ry      coding = 00yyxx
rx, ry, imm coding = iiyyxx

0x00 NOP
0x01 LOAD IMM, r0
0x02 STORE IMM, r0
0x03 LOAD rx, r0
0x04 STORE rx, r0
0x05 MOV rx, ry, imm

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
"""
