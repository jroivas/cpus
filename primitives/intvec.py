
class IntVec:
    def __init__(self, intcnt=4):
        """ Initialize
        """
        self.interrupts = []
        self.intcnt = intcnt
        self.enabled = False

    def isEnabled(self):
        """ Check whether interrupts are enabled
        """
        return self.enabled

    def enable(self):
        """ Enable interrupts
        """
        self.enabled = True

    def disable(self):
        """ Disable interrupts
        """
        self.enabled = False

    def count(self):
        """ Get number of handlers
        """
        return self.intcnt

    def setFlags(self, flags):
        """ Set flags

        >>> i = IntVec()
        >>> i.setFlags(0x111)
        >>> i.isEnabled()
        True
        >>> i.setFlags(0x110)
        >>> i.isEnabled()
        False
        """
        if flags & 0x1 == 0x1:
            self.enabled = True
        else:
            self.enabled = False

    def read(self, mem, mempos, wordsize):
        """ Read the interrupt vector table

        >>> from primitives import Mem
        >>> m = Mem(10)
        >>> i = IntVec()
        >>> i.read(m, 0, 4)
        >>> i.getHandler(0)
        0
        >>> i.getHandler(1)
        4
        >>> i.getHandler(2)
        8
        >>> i.getHandler(3)
        12
        >>> i.read(m, 3, 4)
        >>> i.getHandler(0)
        3
        >>> i.getHandler(3)
        15
        """
        pos = mempos
        self.interrupts = []
        for tmp in xrange(self.intcnt):
            self.interrupts.append(pos)
            pos += wordsize

    def getHandler(self, num):
        """ Get memory position of interrupt handler for specific number
        """
        if num >= 0 and num < self.intcnt:
            pos = self.interrupts[num]
            return pos
    
        return None
