#!/usr/bin/env python

import sys
import os
from cpus import Opcodes

class Assembly:
    
    def __init__(self):
        self.code = []
        self.opcodes = Opcodes()
        self.wordsize = 4

    def readfile(self, filename):
        try:
            f = open(filename, 'r')
            data = f.readlines()
            f.close()
        except:
            data = None

        return data

    def parse(self, data):
        for line in data:
            print line

    def getLabels(self, data):
        labels = {}
        index = 0
        for line in data:
            if ':' in line:
                tmp = line.strip().split(':')
                if tmp:
                    label = tmp[0]
                    if len(tmp) > 1:
                        val = ':'.join(tmp[1:])
                    else:
                        val = ''
                    labels[label] = { 'value': val, 'line': index }
            index += 1
        return labels

    def parseImmediate(self, data):
        return data

    def parseRegs(self, data):
        tmp = data.split(',')
        args = []
        for item in tmp:
            item = item.strip()
            if item:
                args.append(item)
        return args

    def assemble(self, data):
        stub = []
        labels = {}
        pc = 0
        index = 0
        for line in data:
            line = line.strip()
            if ':' in line:
                tmp = line.split(':')
                if tmp:
                    label = tmp[0]
                    if len(tmp) > 1:
                        line = ':'.join(tmp[1:])
                    else:
                        line = ''
                    labels[label] = { 'value': line, 'line': index, 'pos': pc }
            tmp = line.split()
            if tmp:
                pc += self.wordsize
            index += 1

        pc = 0
        for line in data:
            line = line.strip()
            if ':' in line:
                tmp = line.split(':')
                if tmp:
                    if len(tmp) > 1:
                        line = ':'.join(tmp[1:])
                    else:
                        line = ''

            tmp = line.split()
            if tmp:
                cmd = tmp[0]
                rest = ' '.join(tmp[1:])
                    
                if cmd in self.opcodes.rev_opcodes:
                    opcode = self.opcodes.rev_opcodes[cmd]
                else:
                    try:
                        if '0x' in cmd:
                            opcode = int(cmd, 16)
                        else:
                            opcode = int(cmd)
                    except:
                        opcode = 255 # FIXME

                if 'i' == cmd[-1] or cmd == 'B':
                    param = self.parseImmediate(rest)
                else:
                    param = self.parseRegs(rest)
                item = {'opcode': opcode, 'params': param, 'cmd': cmd, 'pos': pc}
                stub.append(item)
                pc += self.wordsize
        return (stub, labels)

    def getLabel(self, name, labels):
        for lab in labels:
            if lab == name:
                return labels[lab]

        return None

    def getRegister(self, name):
        num = name[1:]
        try:
            r = int(num)
            r += 1
            if r > 255:
                r = 255
        except:
            r = 0

        return r

    def getImmediate(self, val, labels):
        lab = self.getLabel(val, labels)
        if lab is not None:
            return lab['pos']

        try:
            if '0x' in lab:
                imm = int(lab, 16)
            else:
                imm = int(lab)
        except:
            imm = 0

        return imm

    def solveLabels(self, stub, labels):
        pc = 0
        for item in stub:
            pars = item['params']
            if type(pars) == str:
                lab = self.getLabel(pars, labels)
                if lab is not None:
                    item['params'] = lab['pos']
            else:
                newpars = []
                for reg in pars: 
                    if reg[0] == 'r':
                        reg = self.getRegister(reg)
                        newpars.append(reg)
                    else:
                        imm = self.getImmediate(reg, labels)
                        newpars.append(imm)
                item['params'] = newpars
        return stub

    def generateRegisters(self, pars):
        x = 0
        y = 0
        i = 0
        tmp = pars[:]
        tmp.reverse()
        if tmp:
            x = tmp.pop()
        if tmp:
            y = tmp.pop()
        if tmp:
            i = tmp.pop()

        x = (x+1) & 0xFF
        y = ((y+1) & 0xFF) << 8
        i = (i & 0xFF) << 16
        return (x | y | i)

    def generateCode(self, stub):
        code = []
        bytecode = []
        for item in stub:
            inst = item['opcode']
            inst = inst & 0xFF

            pars = item['params']
            if type(pars) == list:
                imm = self.generateRegisters(pars)
            else:
                imm = pars
            #print '%x' % inst, imm, pars
            imm = imm & 0xFFFFFF
            imm <<= 8
            bytecode.append(inst)
            code.append(inst | imm)
            immcode = []
            imm >>= 8
            for i in xrange(3):
                immcode.append(imm & 0xFF)
                imm >>= 8
            bytecode += immcode
        return (code, bytecode)

    def writeFile(self, fname, data):
        if os.path.isfile(fname):
            print ('WARNING: Overwriting %s' % fname)
        
        arr = bytearray()
        for code in data:
            arr.append(code)
        f = open(fname, 'wb')
        f.write(arr)
        f.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ('Usage: %s file.asm [outfile]' % sys.argv[0])
        sys.exit(1)
    
    fname = sys.argv[1]
    ofname = None
    if len(sys.argv) > 2:
        ofname = sys.argv[2]

    ass = Assembly()
    data = ass.readfile(fname)
    if data is None:
        print ('Can\'t read file: %s' % (fname))
        sys.exit(1)

    (stub, labels) = ass.assemble(data)
    stub = ass.solveLabels(stub, labels)
    print (stub)
    (code, bytecode) = ass.generateCode(stub)
    #print code
    if ofname is not None:
        for c in code:
            print "%.8x" % c
        ass.writeFile(ofname, bytecode)
    else:
        print stub
        print code
