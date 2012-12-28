
class Stack:
    def __init__(self, pos, mem, wordsize):
        """ Initialize stack
        """
        self.base = pos
        self.pos = pos
        self.mem = mem
        self.size = None
        self.wordsize = wordsize

    def getPos(self):
        """ Get current position of stack
        """
        return self.pos

    def relocate(self, pos):
        """ Relocate stack

        >>> from primitives import Mem
        >>> mymem = Mem(100)
        >>> mymem.setRaw(21, 0xFF)
        >>> s = Stack(20, mymem, 4)
        >>> s.push(1)
        >>> s.push(2)
        >>> s.push(3)
        >>> s.push(4)
        >>> s.pop()
        4
        >>> s.relocate(12)
        >>> s.pop()
        2
        >>> s.pop()
        1
        """
        self.base = pos
        self.pos = pos

    def setSize(self, size):
        """ Set stack size, enables boundary checking
        """
        self.size = size

    def upBoundCheck(self):
        """ Check for upper bound of the stack

        >>> from primitives import Mem
        >>> mymem = Mem(100)
        >>> mymem.setRaw(21, 0xFF)
        >>> s = Stack(20, mymem, 4)
        >>> # Test that we can go beound boundaries
        >>> print '%x' % s.pop()
        ff00
        >>> # Return
        >>> s.push(0)
        >>> s.setSize(16)
        >>> s.pop() #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Stack underflow!
        >>> s.push(42)
        >>> s.pop()
        42
        """
        if self.size is None:
            return True

        if self.pos >= self.base:
            return False

        return True

    def lowBoundCheck(self):
        """ Check for lower bound of the stack

        >>> from primitives import Mem
        >>> mymem = Mem(100)
        >>> s = Stack(20, mymem, 4)
        >>> s.setSize(16)
        >>> s.push(10)
        >>> s.push(9)
        >>> s.push(8)
        >>> s.push(7)
        >>> s.push(6) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Stack overflow!
        """
        if self.size is None:
            return True

        bottom = self.base - self.size
        if self.pos <= bottom:
            return False

        return True

    def push(self, data):
        """ Push data to stack

        >>> from primitives import Mem
        >>> mymem = Mem(100)
        >>> s = Stack(20, mymem, 4)
        >>> s.push(10)
        >>> s.push(9)
        >>> mymem.getData(20-4)
        10
        >>> mymem.getData(20-4*2)
        9
        """
        if not self.lowBoundCheck():
            raise IndexError('Stack overflow!')
        self.pos -= self.wordsize
        self.mem.setData(self.pos, data, self.wordsize)

    def pop(self):
        """ Pop data back from stack

        >>> from primitives import Mem
        >>> mymem = Mem(100)
        >>> s = Stack(20, mymem, 4)
        >>> s.push(10)
        >>> s.push(9)
        >>> s.push(4)
        >>> s.pop()
        4
        >>> s.pop()
        9
        >>> s.pop()
        10
        """
        if not self.upBoundCheck():
            raise IndexError('Stack underflow!')
        data = self.mem.getData(self.pos, self.wordsize)
        self.pos += self.wordsize
        return data
