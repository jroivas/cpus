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
        try:
            if '0x' in data:
                imm = int(data, 16)
            else:
                imm = int(data)
        except:
            imm = data
        return imm

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
        datasect = []
        labels = {}
        pc = 0
        dpc = 0
        index = 0
        base = 0
        mode = 'code'

        ## FIXME Goes thorough the code three times,
        ## need a better and cleaner implementation
        for line in data:
            line = line.strip()
            if not line:
                index += 1
                continue
            if line == '.code':
                mode = 'code'
                continue
            elif line == '.data':
                mode = 'data'
                continue
            elif line[:5] == '.base':
                b = line[6:]
                base = self.parseImmediate(b)
                continue

            if '#' in line:
                pos = line.index('#')
                line = line[:pos].strip()
            if ':' in line:
                tmp = line.split(':')
                if tmp:
                    label = tmp[0]
                    if len(tmp) > 1:
                        line = ':'.join(tmp[1:])
                    else:
                        line = ''
                    if mode == 'code':
                        labels[label] = { 'value': line, 'line': index, 'pos': pc }
                    elif mode == 'data':
                        labels[label] = { 'value': line, 'line': index, 'pos': base + dpc }
            datasize = self.wordsize
            tmp = line.split()
            if tmp:
                ucmd = tmp[0].upper()
                rest = tmp[1:]
                if len(ucmd) == 2 and ucmd[0] == 'D':
                    if ucmd[1] == 'B':
                        datasize = 1
                    elif ucmd[1] == 'W':
                        datasize = 2
                    elif ucmd[1] == 'D':
                        datasize = 4
                    elif ucmd[1] == 'Q':
                        datasize = 8
                    elif ucmd[1] == 'T':
                        datasize = 0

                    if datasize == 0:
                        string = False
                        dataval = bytearray()
                        for c in rest:
                            if not string and c == '"':
                                string = True
                            elif string and c == '"':
                                datasize += 1
                                dataval.append(0)
                                string = False
                            elif string:
                                datasize += 1
                                dataval.append(c)
            tmp = line.split()
            if tmp:
                if mode == 'code':
                    pc += datasize
                elif mode == 'data':
                    dpc += datasize
            index += 1

        if base == 0:
            base = pc

        pc = 0
        dpc = 0
        for line in data:
            line = line.strip()
            if not line:
                index += 1
                continue
            if line == '.code':
                mode = 'code'
                continue
            elif line == '.data':
                mode = 'data'
                continue
            elif line[:5] == '.base':
                continue
            if '#' in line:
                pos = line.index('#')
                line = line[:pos].strip()
            if ':' in line:
                tmp = line.split(':')
                if tmp:
                    label = tmp[0]
                    if len(tmp) > 1:
                        line = ':'.join(tmp[1:])
                    else:
                        line = ''
                    #if mode == 'code':
                    #    labels[label] = { 'value': line, 'line': index, 'pos': pc }
                    if mode == 'data':
                        labels[label] = { 'value': line, 'line': index, 'pos': base + dpc }
            datasize = self.wordsize
            tmp = line.split()
            if tmp:
                ucmd = tmp[0].upper()
                rest = tmp[1:]
                if len(ucmd) == 2 and ucmd[0] == 'D':
                    if ucmd[1] == 'B':
                        datasize = 1
                    elif ucmd[1] == 'W':
                        datasize = 2
                    elif ucmd[1] == 'D':
                        datasize = 4
                    elif ucmd[1] == 'Q':
                        datasize = 8
                    elif ucmd[1] == 'T':
                        datasize = 0

                    if datasize == 0:
                        string = False
                        dataval = bytearray()
                        for c in rest:
                            if not string and c == '"':
                                string = True
                            elif string and c == '"':
                                datasize += 1
                                dataval.append(0)
                                string = False
                            elif string:
                                datasize += 1
                                dataval.append(c)
            tmp = line.split()
            if tmp:
                if mode == 'code':
                    pc += datasize
                elif mode == 'data':
                    dpc += datasize
            index += 1

        pc = 0
        dpc = 0
        mode = 'code'
        for line in data:
            line = line.strip()
            if not line:
                index += 1
                continue
            if line == '.code':
                mode = 'code'
                continue
            elif line == '.data':
                mode = 'data'
                continue
            elif line[:5] == '.base':
                continue

            if '#' in line:
                pos = line.index('#')
                line = line[:pos].strip()
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
                ucmd = tmp[0].upper()
                rest = ' '.join(tmp[1:])
                    
                if cmd in self.opcodes.aliases:
                    cmd = self.opcodes.aliases[cmd]
                    ucmd = cmd.upper()

                datasize = 4
                if ucmd in self.opcodes.rev_upper_opcodes:
                    opcode = self.opcodes.rev_upper_opcodes[ucmd]
                elif len(cmd) == 2 and ucmd[0] == 'D':
                    opcode = 'data'
                    datasize = 4
                    if ucmd[1] == 'B':
                        datasize = 1
                    elif ucmd[1] == 'W':
                        datasize = 2
                    elif ucmd[1] == 'D':
                        datasize = 4
                    elif ucmd[1] == 'Q':
                        datasize = 8
                    elif ucmd[1] == 'T':
                        datasize = 0

                    if datasize > 0:
                        try:
                            if '0x' in rest:
                                dataval = int(rest, 16)
                            else:
                                dataval = int(rest)
                        except:
                            dataval = 0
                    else:
                        string = False
                        dataval = bytearray()
                        for c in rest:
                            if not string and c == '"':
                                string = True
                            elif string and c == '"':
                                datasize += 1
                                dataval.append(0)
                                string = False
                            elif string:
                                datasize += 1
                                dataval.append(c)
                else:
                    try:
                        if '0x' in cmd:
                            opcode = int(cmd, 16)
                        else:
                            opcode = int(cmd)
                    except:
                        opcode = 'invalid' # FIXME

                if 'i' == cmd[-1]:
                    param = self.parseImmediate(rest)
                elif opcode == 'data':
                    param = self.parseImmediate(rest)
                else:
                    param = self.parseRegs(rest)

                if mode == 'code':
                    item = {'opcode': opcode, 'params': param, 'cmd': cmd, 'pos': pc, 'datasize': datasize}
                    stub.append(item)
                elif mode == 'data':
                    if opcode == 'data':
                        item = {'size': datasize, 'pos': base + dpc, 'val': dataval}
                        datasect.append(item)
                    else:
                        datasize = 0

                if mode == 'code':
                    if opcode == 'data':
                        pc += datasize
                    else:
                        pc += self.wordsize
                elif mode == 'data':
                    dpc += datasize
        return (stub, datasect, labels, base)

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

        lab = val
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
                elif pars == '.':
                    item['params'] = item['pos']
            elif type(pars) == int:
                pass
            else:
                newpars = []
                i = 0
                for reg in pars: 
                    if reg[0] == 'r':
                        reg = self.getRegister(reg)
                        newpars.append(reg)
                    else:
                        if item['cmd'][-1].upper() != 'I' and reg != '0' and reg != 0 and i < 2 and reg[0] != 'r':
                            raise ValueError('Expected register, got: %s %s' % (reg, item))
                        imm = self.getImmediate(reg, labels)
                        newpars.append(imm)
                    i += 1
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

        x = x & 0xFF
        y = (y & 0xFF) << 8
        if i != (i & 0xFF):
            raise ValueError('Immediate value truncated: %x vs. %x' % (i, i & 0xFF) )
        i = (i & 0xFF) << 16
        return (x | y | i)

    def generateCode(self, stub):
        code = []
        bytecode = []
        for item in stub:
            inst = item['opcode']
            pars = item['params']
            data = False
            if inst == 'data':
                data = True
                imm = pars
            else:
                inst = inst & 0xFF

                if type(pars) == list:
                    imm = self.generateRegisters(pars)
                else:
                    imm = pars

            imm = imm & 0xFFFFFF
            if inst == 'data':
                immcode = []
                code.append(imm)
                size = item['datasize']
                while size > 0:
                    immcode.append(imm & 0xFF)
                    imm >>= 8
                    size -= 1
            else:
                imm <<= 8
                bytecode.append(inst)
                code.append(inst | imm)
                immcode = []
                imm >>= 8
                for i in xrange(self.wordsize-1):
                    immcode.append(imm & 0xFF)
                    imm >>= 8
            bytecode += immcode
        return (code, bytecode)

    def generateData(self, data):
        bindata = bytearray()
        for item in data:
            val = item['val']
            size = item['size']
            if type(val) != bytearray:
                newval = bytearray()
                while size > 0:
                    newval.append(val & 0xFF)
                    val >>= 8
                    size -= 1
                val = newval
            bindata = bindata + val
            
        return bindata

    def writeFile(self, fname, code, data, base=0):
        if os.path.isfile(fname):
            print ('WARNING: Overwriting %s' % fname)
        
        arr = bytearray()
        for opcode in code:
            arr.append(opcode)

        header_size = 12
        datapos = len(arr) + header_size

        header = bytearray()
        header.append('R')
        header.append('E')
        header.append('0')
        header.append('1')
        tmp = datapos
        for i in xrange(4):
            header.append(tmp & 0xFF)
            tmp >>= 8
        tmp = base
        for i in xrange(4):
            header.append(tmp & 0xFF)
            tmp >>= 8
        f = open(fname, 'wb')
        f.write(header)
        f.write(arr)
        f.write(data)
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

    (stub, data, labels, base) = ass.assemble(data)
    print labels
    print base
    print data
    stub = ass.solveLabels(stub, labels)
    print (stub)
    (code, bytecode) = ass.generateCode(stub)
    (bindata) = ass.generateData(data)
    if ofname is not None:
        print ("Code:")
        for c in code:
            print ("%.8x" % c)
        print ("Data:")
        binstr = ''
        i = 0
        for c in bindata:
            binstr += '%.2x ' % c 
            i += 1
            if i % 16 == 0:
                binstr += '\n'
        print (binstr)
        ass.writeFile(ofname, bytecode, bindata, base)
    else:
        print stub
        print code
