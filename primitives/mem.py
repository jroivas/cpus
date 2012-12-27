import math

class CPUMem:
    """ Contains main memory for CPU
    """
    _wordsize = 4
    
    def __init__(self, size=0):
        """ Initialize the memory

        @param size Size of memory in bytes
        """
        self._size = size
        (self._internal_size, dummy) = self.calcInternal(size)
        self._submem = None
        self.reset()
        self._specials = {}

    def addSpecial(self, mem, handler_get, handler_set):
        """ Add special handler for certain memory location
        @param mem Memory location
        @param handler_get Callback for get
        @param handler_set Callback for set

        >>> m = CPUMem(100)
        >>> class TestIO:
        ...  def __init__(self):
        ...   self.vals = {}
        ...  def dummy_get(self, pos):
        ...   print "get at %s" % (pos)
        ...   if pos in self.vals:
        ...     return self.vals[pos]
        ...   return 42
        ...  def dummy_set(self, pos, a):
        ...   print "set at %s, val %s" % (pos, a)
        ...   self.vals[pos] = a
        >>> myio = TestIO()
        >>> m.addSpecial(10, myio.dummy_get, None)
        >>> m.addSpecial(11, None, myio.dummy_set)
        >>> m.addSpecial(12, myio.dummy_get, myio.dummy_set)
        >>> print m.get(0)
        0
        >>> print m.get(10*4)
        get at 10
        42
        >>> m.set(10*4, 55)
        get at 10
        >>> m.set(11*4, 6)
        set at 11, val 6
        >>> print m.get(11*4)
        0
        >>> print m.get(12*4)
        get at 12
        42
        >>> m.set(12*4, 7)
        get at 12
        set at 12, val 7
        >>> print m.get(12*4)
        get at 12
        7
        >>> print m.get(13*4)
        0
        >>> m.set(13*4, 5)
        >>> print m.get(13*4)
        5
        >>> m.addSpecial(12, myio.dummy_get, myio.dummy_set) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Special memory handler already registered to 12
        """
        if mem in self._specials:
            raise ValueError("Special memory handler already registered to %s" % mem)
        self._specials[mem] = (handler_get, handler_set)

    def subMemory(self, mem, pos):
        """ Define this as a submemory on other memory instance
        @param mem Another memory instance
        @param pos Position in real memory
        """
        self._submem = mem
        (self._sub_int_pos, dummy) = self.calcInternal(pos)
        self._sub_pos = pos

    def reset(self):
        """ Reset memory
        Initializes memory to given size
        """
        self._data = []
        for i in range(self._internal_size):
            self._data.append(0)

    def calcInternal(self, pos):
        """ Calculate internal position
        @param pos Global pos
        @returns Internal pos
        """
        return (int(math.ceil((pos + 1.0) / self._wordsize)), pos % self._wordsize)

    def enlarge(self, size):
        """ Enlarge memory size

        @param size New memory size
        """
        (self._internal_size, dummy) = self.calcInternal(size)
        while len(self._data) < self._internal_size:
            self._data.append(0)

    def setRaw(self, int_pos, data):
        """ Set raw memory value to data
        @param pos Index
        @param data Data to set

        >>> m = CPUMem(100)
        >>> m.setRaw(0, 100)
        >>> m.setRaw(1, 42)
        >>> m.getRaw(0)
        100
        >>> m.getRaw(1)
        42
        >>> m2 = CPUMem()
        >>> m2.setRaw(0, 100)
        >>> m2.setRaw(1, 200)
        >>> m2.setRaw(2, 300)
        >>> m2.setRaw(2000, 123456)
        >>> m2.getRaw(0)
        100
        >>> m2.getRaw(1)
        200
        >>> m2.getRaw(2)
        300
        >>> m2.getRaw(1999)
        0
        >>> m2.getRaw(2000)
        123456
        >>> m2.getRaw(2001) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: list index out of range
        >>> m.setRaw(9, 10)
        >>> m.setRaw(11, 42)
        >>> m2 = CPUMem()
        >>> m2.subMemory(m, 8*4)
        >>> print m2.getRaw(0)
        10
        >>> print m2.getRaw(1)
        0
        >>> print m2.getRaw(2)
        42
        >>> m3 = CPUMem(10)
        >>> m3.subMemory(m, 0)
        >>> print m3.get(0)
        100
        >>> print m3.get(1)
        0
        >>> print m3.get(9)
        0
        >>> print m3.get(10)
        0
        >>> print m3.get(11) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Sub memory size limit hit!
        """
        if self._submem is not None:
            if self._size > 0 and int_pos > self._internal_size:
                raise IndexError("Sub memory size limit hit!")
            return self._submem.setRaw(self._sub_int_pos + int_pos, data)
        if self._size == 0:
            self.enlarge(int_pos * self._wordsize)
        if self._internal_size < int_pos:
            raise IndexError("Given internal memory position is invalid: %s, max size: %s" % (int_pos, self._internal_size))
        if int_pos < 0:
            raise IndexError("Memory position needs to be positive number, got: %s" % (int_pos))

        if int_pos in self._specials:
            (hget, hset) = self._specials[int_pos]
            if hset is not None:
                return hset(int_pos, data)
            return
        self._data[int_pos] = data

    def getRaw(self, int_pos):
        """ Get data from internal pos
        @param pos Index
        @returns Data
        """
        if self._submem is not None:
            if self._size > 0 and int_pos > self._internal_size:
                raise IndexError("Sub memory size limit hit!")
            return self._submem.getRaw(self._sub_int_pos + int_pos)
        if self._internal_size < int_pos:
            raise IndexError("Given internal memory position is invalid: %s, max size: %s" % (int_pos, self._internal_size))
        if int_pos < 0:
            raise IndexError("Memory position needs to be positive number, got: %s" % (int_pos))

        if int_pos in self._specials:
            (hget, hset) = self._specials[int_pos]
            if hget is not None:
                return hget(int_pos)
            return 0
        return self._data[int_pos]

    def set(self, pos, data, size=0xFF):
        """ Set memory value to data
        @param pos Index
        @param data Data to set
        @param size Data size

        >>> m = CPUMem(100)
        >>> m.set(0, 0xaa)
        >>> print ("%x" % m.getRaw(0))
        aa
        >>> m.set(1, 0xbb)
        >>> print ("%x" % m.getRaw(0))
        bbaa
        >>> m.set(2, 0xcc)
        >>> m.set(3, 0xdd)
        >>> m.set(4, 0xde)
        >>> print ("%x" % m.getRaw(0))
        ddccbbaa
        >>> print ("%x" % m.getRaw(1))
        de
        >>> m.set(-1, 0xde) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Memory position needs to be positive number, got: -1
        >>> m.set(200, 0xde) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Given memory position is invalid: 200, max size: 100
        >>> m.set(50, 42)
        >>> m.set(51, 43)
        >>> m.set(60, 44)
        >>> m2 = CPUMem()
        >>> m2.subMemory(m, 50)
        >>> print m2.get(0)
        42
        >>> print m2.get(1)
        43
        >>> print m2.get(2)
        0
        >>> print m2.get(10)
        44
        >>> m2.set(20, 99)
        >>> print m.get(50+20)
        99
        """
        if self._submem is not None:
            if self._size > 0 and pos > self._size:
                raise IndexError("Sub memory size limit hit!")
            return self._submem.set(self._sub_pos + pos, data, size)

        if self._size == 0:
            self.enlarge(pos)
        if self._size < pos:
            raise IndexError("Given memory position is invalid: %s, max size: %s" % (pos, self._size))
        if pos < 0:
            raise IndexError("Memory position needs to be positive number, got: %s" % (pos))
    
        (int_pos, int_index) = self.calcInternal(pos)
        # Decrease because indexing is from 0, this is size
        int_pos -= 1
        tmp = self.getRaw(int_pos)
        #tmp = self._data[int_pos] 
        data = data & size

        shifter = (int_index*8)
        size <<= shifter
        data <<= shifter
        tmp = tmp & (~size)
        tmp = tmp | data
        self.setRaw(int_pos, tmp)
        #self._data[int_pos]  = tmp

    def get(self, pos, size=0xFF):
        """ Get memory value
        @param pos Index
        @param size Data size

        >>> m = CPUMem(100)
        >>> m.set(0, 0xaa)
        >>> print ("%x" % m.get(0))
        aa
        >>> print ("%x" % m.get(1))
        0
        >>> m.set(3, 0x42)
        >>> print ("%x" % m.get(3))
        42
        """
        if self._submem is not None:
            if self._size > 0 and pos > self._size:
                raise IndexError("Sub memory size limit hit!")
            return self._submem.get(self._sub_pos + pos, size)

        if self._size < pos:
            #if self._size == 0:
            #    return 0
            raise IndexError("Given memory position is invalid: %s, max size: %s" % (pos, self._size))
        if pos < 0:
            raise IndexError("Memory position needs to be positive number, got: %s" % (pos))
    
        (int_pos, int_index) = self.calcInternal(pos)
        int_pos -= 1
        #print int_pos
        #tmp = self._data[int_pos] 
        tmp = self.getRaw(int_pos)
        shifter = (int_index*8)
        size <<= shifter
        tmp = tmp & size
        tmp >>= shifter
        return tmp
