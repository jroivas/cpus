
class IntVec:
    def __init__(self, intcnt=4):
        self.interrupts = []
        self.intcnt = intcnt
        self.enabled = False

    def isEnabled(self):
        return self.enabled

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def count(self):
        return self.intcnt

    def setFlags(self, flags):
        if flags & 0x1 == 0x1:
            self.enabled = True
        else:
            self.enabled = False

    def read(self, mem, mempos, wordsize):
        pos = mempos
        self.interrupts = []
        for tmp in xrange(self.intcnt):
            #data = mem.getData(pos, wordsize)
            #self.interrupts.append(data)
            self.interrupts.append(pos)
            pos += wordsize

    def getHandler(self, num):
        if num >= 0 and num < self.intcnt:
            pos = self.interrupts[num]
            return pos
    
        return None
