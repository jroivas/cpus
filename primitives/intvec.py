
class IntVec:
    def __init__(self, intcnt=8):
        self.interrupts = []
        self.intcnt = intcnt
        self.enabled = False

    def isEnabled(self):
        return self.enabled

    def count(self):
        return self.intcnt

    def setFlags(self, flags):
        if flags & 0x1 == 0x1:
            self.enabled = True
        else:
            self.enabled = False

    def read(self, mem, mempos, wordsize):
        pos = mempos
        for tmp in xrange(self.intcnt):
            data = mem.getData(pos, wordsize)
            self.interrupts.append(data)
            pos += wordsize

    def getHandler(self, num):
        if num >= 0 and num < intcnt:
            pos = self.interrupts[num]
            return pos
    
        return None

    def run(self, num):
        handler = self.getHandler(num)
        #if handler is not None:
