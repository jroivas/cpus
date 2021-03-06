import math
import sys
if sys.version >= '3':
    xrange = range

class Mem(object):
    """ Contains main memory for CPU
    """
    _pagesize = 0x1000
    
    def __init__(self, size=0):
        """ Initialize the memory

        @param size Size of memory in bytes
        """
        self._size = size
        if size == 0:
            self._autosize = True
        else:
            self._autosize = False
        self._submem = None
        self.reset()
        self._specials = {}

    def getSize(self):
        """ Get memory size
        """
        return self._size

    def reset(self):
        """ Reset memory
        Initializes memory to given size
        """
        self._datas = {}

    def addSpecial(self, mem, handler_get, handler_set):
        """ Add special handler for certain memory location
        @param mem Memory location
        @param handler_get Callback for get
        @param handler_set Callback for set

        >>> m = Mem(100)
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
        >>> print m.getRaw(0)
        0
        >>> print m.getRaw(10)
        get at 10
        42
        >>> m.setRaw(10, 55)
        >>> m.setRaw(11, 6)
        set at 11, val 6
        >>> print m.getRaw(11)
        0
        >>> print m.getRaw(12)
        get at 12
        42
        >>> m.setRaw(12, 7)
        set at 12, val 7
        >>> print m.getRaw(12)
        get at 12
        7
        >>> print m.getRaw(13)
        0
        >>> m.setRaw(13, 5)
        >>> print m.getRaw(13)
        5
        >>> m.addSpecial(12, myio.dummy_get, myio.dummy_set) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Special memory handler already registered to 12
        """
        if mem in self._specials:
            raise ValueError("Special memory handler already registered to %s" % mem)
        self._specials[mem] = (handler_get, handler_set)

    def getSpecial(self, pos):
        """ Get special location
        @pos Position of special memory
        """

        return self._specials.get(pos, None)
        try:
            return self._specials[pos]
        except KeyError:
            return None
        """
        for k in self._specials.keys():
            if pos >= k and pos < (k + 4):
                return self._specials[k]
        """

    def subMemory(self, mem, pos):
        """ Define this as a submemory on other memory instance
        @param mem Another memory instance
        @param pos Position in real memory
        """
        self._submem = mem
        self._sub_pos = pos

    def enlarge(self, size):
        """ Enlarge memory size

        @param size New memory size
        """
        self._size = size

    def setData(self, pos, data, size=4):
        """ Set data, can be sized as 1..size bytes
        @param pos Position
        @param data data
        @param size Maximum data length in bytes

        >>> m = Mem(100)
        >>> m.setData(4, 0x123456)
        >>> print "%x" % m.getData(4, 4)
        123456
        >>> m.setData(8, 0x12345678)
        >>> print "%x" % m.getData(8, 4)
        12345678
        >>> print "%x" % m.getData(8, 2)
        5678
        """
        tmp = data
        cnt = 0
        while tmp:
            bval = tmp & 0xFF
            tmp >>= 8
            self.setRaw(pos, bval)
            pos += 1
            cnt += 1
            if cnt > size:
                raise ValueError('Gave too big number: %s, %s > %s' % (data, cnt, size))
                break

    def getData(self, pos, size=1):
        """ Get data with size
        @param pos Position
        @param size Size in bytes
        @returns Data
        """
        res = 0
        while size > 0:
            tmp = self.getRaw(pos + size - 1)
            res = res | tmp
            size -= 1
            if size > 0:
                res <<= 8
        return res

    def getBlock(self, pos, size=1):
        """ Get memory blocks at given position and given size
        May return multiple blocks if size is big enough or boundaries crossed

        >>> m = Mem(0x1000*5+2)
        >>> m.setData(0xffe, 0x12345678)
        >>> len(m.getBlock(0xffe, 4))
        2
        >>> len(m.getBlock(0xff0, 4))
        1
        >>> len(m.getBlock(0x1010, 4))
        1
        >>> len(m.getBlock(0xffe, 0x1020))
        3
        """
        res = []
        start = int(pos /  self._pagesize)
        items = int((pos + size) / self._pagesize)
        mod = (pos + size) % self._pagesize
        if start == 0:
            items += 1
        pos = start
        for i in xrange(items):
            try:
                res.append((pos, self._datas[pos]))
            except:
                res.append((pos, None))
            pos += 1
        return res

    def getPage(self, pos, create=False):
        """ Get page index

        >>> m = Mem(0x1000*3)
        >>> m.getPage(100)
        (None, None)
        >>> (page, index) = m.getPage(100, create=True)
        >>> index
        100
        >>> (page, index) = m.getPage(0x1002, create=True)
        >>> index
        2
        """
        index = int(pos / self._pagesize)
        if not index in self._datas:
            if not create:
                return (None, None)
            self._datas[index] = bytearray(self._pagesize)
        subindex = (pos) - (index * self._pagesize)

        return (self._datas[index], subindex)

    def setRaw(self, pos, data):
        """ Set raw memory value at position to given data
        @param pos Index
        @param data Data to set

        >>> m = Mem(100)
        >>> m.setRaw(0, 100)
        >>> m.setRaw(1, 42)
        >>> m.getRaw(0)
        100
        >>> m.getRaw(1)
        42
        >>> m2 = Mem()
        >>> m2.setRaw(0, 100)
        >>> m2.setRaw(1, 200)
        >>> m2.setData(2, 300)
        >>> m2.setData(2000, 123456)
        >>> m2.getRaw(0)
        100
        >>> m2.getRaw(1)
        200
        >>> m2.getData(2, 2)
        300
        >>> m2.getRaw(1999)
        0
        >>> m2.getData(2000, 3)
        123456
        >>> m2.getRaw(2010) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Given memory position is invalid: 2010, max size: ...
        >>> m.setRaw(9, 10)
        >>> m.setRaw(11, 42)
        >>> m2 = Mem()
        >>> m2.subMemory(m, 9)
        >>> print m2.getRaw(0)
        10
        >>> print m2.getRaw(1)
        0
        >>> print m2.getRaw(2)
        42
        >>> m3 = Mem(10)
        >>> m3.subMemory(m, 0)
        >>> print m3.getRaw(0)
        100
        >>> print m3.getRaw(1)
        42
        >>> print m3.getRaw(9)
        10
        >>> print m3.getRaw(10)
        0
        >>> print m3.getRaw(11) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        IndexError: Sub memory size limit hit!
        """
        if self._submem is not None:
            if self._size > 0 and pos > self._size:
                raise IndexError("Sub memory size limit hit!")
            return self._submem.setRaw(self._sub_pos + pos, data)

        if self._size == 0:
            self.enlarge(pos + 1)

        special = self.getSpecial(pos)
        if self._size < (pos + 1) and special is None:
            if self._autosize:
                self.enlarge(pos + 1)
            else:
                #print ("%s" % pos, self._specials.keys())
                raise IndexError("Given memory position is invalid: %s, max size: %s" % (pos, self._size))
        if pos < 0:
            raise IndexError("Memory position needs to be positive number, got: %s" % (pos))

        if special is not None:
            (hget, hset) = special
            if hset is not None:
                return hset(pos, data)
            return

        (page, subindex) = self.getPage(pos, create=True)
        page[subindex] = data

    def getRaw(self, pos):
        """ Get data from specified position
        @param pos Index
        @returns Data
        """
        if self._submem is not None:
            if self._size > 0 and pos > self._size:
                raise IndexError("Sub memory size limit hit!")
            return self._submem.getRaw(self._sub_pos + pos)

        special = self.getSpecial(pos)
        if self._size < pos and special is None:
            raise IndexError("Given memory position is invalid: %s, max size: %s" % (pos, self._size))
        if pos < 0:
            raise IndexError("Memory position needs to be positive number, got: %s" % (pos))

        if special is not None:
            (hget, hset) = special
            if hget is not None:
                return hget(pos)
            return 0

        (page, subindex) = self.getPage(pos)
        if page == None:
            return 0
        return page[subindex]
