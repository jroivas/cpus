from primitives import Mem

class MMU():
    def __init__(self, mem, size=0):
        """ Initialize MMU
        """
        self._enabled = False
        self._mem = mem
        self._wordsize = 4
        self._table = []

    def enable(self):
        """ Enables MMU
        """
        self._enabled = True

    def disable(self):
        """ Disables MMU
        """
        self._enabled = False

    def getEntries(self, entries, startpos=None):
        """ Get page entries and parse them, handle recursively

        >>> from primitives import Mem
        >>> m = Mem(1024*100)
        >>> m.setData(0, 0x00000100, 4)
        >>> m.setData(4, 0x00001100, 4)
        >>> m.setData(8, 0x00002100, 4)
        >>> m.setData(12, 0x00003100, 4)
        >>> u = MMU(m)
        >>> entries = [(4096, MMU.Flags(solved={'execute': False, 'ok': True, 'size1': True, 'size2': False, 'write': False, 'subtable': True, 'userspace': False, 'size': 64}), 0),
        ... (32768, MMU.Flags(solved={'execute': False, 'ok': True, 'size1': True, 'size2': False, 'write': False, 'subtable': False, 'userspace': False, 'size': 64}), 65536),
        ... (0, MMU.Flags(solved={'execute': False, 'ok': True, 'size1': False, 'size2': False, 'write': False, 'subtable': False, 'userspace': False, 'size': 4}), 131072)]
        >>> u.getEntries(entries)
        [(0, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 0), (4096, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 4096), (8192, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 8192), (12288, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 12288), (32768, execute=False,ok=True,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False, 65536), (0, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 131072)]
        """
        if startpos is None:
            startpos = 0
        subs = []
        for (addr, flags, pos) in entries:
            if flags['subtable']:
                size = flags['size'] * 1024 / 4
                if flags['ok']:
                    #tmp = self.readTable(addr, size, startpos)
                    tmp = self.readTable(pos, size, pos)
                    entries = self.getEntries(tmp, startpos)
                    subs += entries
                    startpos += flags['size'] * 1024
            else:
                #if addr > 0 and flags['size'] > 0:
                if flags['ok']:
                    #subs.append((addr, flags, startpos + pos))
                    subs.append((addr, flags, pos))
        return subs

    def initialize(self, tablepos, tablesize):
        """ Initializes MMU with a initial page
        Does recursive parsing

        >>> from primitives import Mem
        >>> m = Mem(1024*100)
        >>> u = MMU(m)
        >>> # Subtable, starts at phys 4k
        >>> m.setData(10, 0x00001111, 4)
        >>> # Page, virtual start at 32k, size 64k
        >>> m.setData(14, 0x00008110, 4)
        >>> # Page, virtual start at 98k, size 4k
        >>> m.setData(18, 0x00018100, 4)
        >>> for i in xrange(1023):
        ...   m.setData(0x1000 + i, 0)
        >>> # Page at 8k, size 4k
        >>> m.setData(0x1000, 0x00002100, 4)
        >>> # Page at 12k, size 1M 
        >>> m.setData(0x1004, 0x00003120, 4)
        >>> u.initialize(10, 3)
        [(8192, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 4194304), (12288, execute=False,ok=True,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False, 4198400), (32768, execute=False,ok=True,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False, 65536), (98304, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 131072)]
        """
        entries = self.readTable(tablepos, tablesize)
        self._table = self.getEntries(entries)
        return self._table

    def readTable(self, tablepos, tablesize, pos=None):
        """ Reads table from memory

        >>> from primitives import Mem
        >>> m = Mem(1024*100)
        >>> u = MMU(m)
        >>> # Subtable, starts at phys 4k
        >>> m.setData(10, 0x00001111, 4)
        >>> # Page, starts at 32k, size 64k
        >>> m.setData(14, 0x00008110, 4)
        >>> for i in xrange(1023):
        ...   m.setData(0x1000 + i, 0)
        >>> tmp = u.readTable(10, 3)
        >>> tmp[0][0]
        4096
        >>> tmp[1][0]
        32768
        >>> tmp[2][0]
        0
        >>> tmp[0][1]
        execute=False,ok=True,size=64,size1=True,size2=False,subtable=True,userspace=False,write=False
        >>> tmp[1][1]
        execute=False,ok=True,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False
        >>> tmp[2][1]
        execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False
        >>> tmp[0]
        (4096, execute=False,ok=True,size=64,size1=True,size2=False,subtable=True,userspace=False,write=False, 0)
        >>> tmp[1]
        (32768, execute=False,ok=True,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False, 65536)
        >>> tmp[2]
        (0, execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 131072)
        """
        datas = []
        if pos is None:
            pos = 0
        for index in xrange(tablesize):
            tmp = self._mem.getData(tablepos + index * self._wordsize, self._wordsize)
            (pos, res) = self.readEntry(tmp, pos)
            datas.append(res)

        return datas

    def readEntry(self, data, pos=0):
        """ Read entry from one page table item data

        >>> m = Mem()
        >>> u = MMU(m)
        >>> u.readEntry(0x00000000)
        (4096, (0, execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 0))
        >>> u.readEntry(0x00001000)
        (4096, (4096, execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 0))
        >>> u.readEntry(0x00001111)
        (65536, (4096, execute=False,ok=True,size=64,size1=True,size2=False,subtable=True,userspace=False,write=False, 0))
        >>> u.readEntry(0x00001022)
        (1048576, (4096, execute=True,ok=False,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False, 0))
        >>> u.readEntry(0x00002FFF)
        (67108864, (8192, execute=True,ok=True,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True, 0))
        >>> u.readEntry(0xFFFFFFFF)
        (67108864, (4294963200, execute=True,ok=True,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True, 0))
        >>> u.readEntry(0)
        (4096, (0, execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 0))
        """
        flags = MMU.Flags(data & 0xFFF)
        vaddr = data & 0xFFFFF000

        return (pos + flags['size'] * 1024, (vaddr, flags, pos))

    def getRange(self, item):
        addr = item[0]
        flags = item[1]
        pos = item[2]
        endaddr = addr + (flags['size'] * 1024)
        return (addr, endaddr, pos)

    def virtToPhys(self, pos):
        """ Converts virtual memory location to physical

        >>> from primitives import Mem
        >>> m = Mem(1024*100)
        >>> u = MMU(m)
        >>> # Page, virtual start at 24, size 4k (0x1000)
        >>> m.setData(10, 0x00006100, 4)
        >>> # Subtable, starts at phys 4k (0x1000)
        >>> m.setData(14, 0x00001101, 4)
        >>> # Page, virtual start at 32k, size 64k (0x10000)
        >>> m.setData(18, 0x00008110, 4)
        >>> # Page, virtual start at 96, size 4k (0x1000)
        >>> m.setData(22, 0x00018100, 4)
        >>> # Page at virtual 8k, size 4k (0x1000)
        >>> m.setData(0x1000, 0x00002100, 4)
        >>> # Page at virtual 1126k, size 1M 
        >>> m.setData(0x1004, 0x00113120, 4)
        >>> u.initialize(10, 4)
        [(24576, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 0), (8192, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 4096), (1126400, execute=False,ok=True,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False, 8192), (32768, execute=False,ok=True,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False, 8192), (98304, execute=False,ok=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False, 73728)]
        >>> u.virtToPhys(0x8000) == (0x2000)
        True
        >>> u.virtToPhys(0x8000)
        8192
        >>> u.virtToPhys(0x8001)
        8193
        >>> u.virtToPhys(0x18000) == (0x2000 + 0x10000)
        True
        >>> u.virtToPhys(0x18000)
        73728
        >>> u.virtToPhys(0x18010) == (0x2000 + 0x10000 + 0x10)
        True
        >>> u.virtToPhys(0x19000) == (0x2000 + 0x10000 + 0x1000)
        True
        >>> u.virtToPhys(0x19001)
        >>> u.virtToPhys(0x1A000)
        >>> u.virtToPhys(0x18fff) == (0x2000 + 0x10000 + 0xfff)
        True
        """
        for item in self._table:
            (a, b, c) = self.getRange(item)
            if a <= pos and pos <= b:
                index = (pos - a)
                phys = c + index
                return phys
        return None

        raise IndexError('Page not mapped!')

    def setData(self, pos, data, size=4):
        if self._enabled:
            pass
        else:
            self._mem.setData(pos, data, size)

    def getData(self, pos, size=1):
        if self._enabled:
            pass
        else:
            return self._mem.getData(pos, size)

    def setRaw(self, pos, data):
        if self._enabled:
            pass
        else:
            self._mem.setRaw(pos, data)

    def getRaw(self, pos):
        if self._enabled:
            pass
        else:
            self._mem.getRaw(pos)
        
    class Flags:
        def __init__(self, flags=0, solved=None):
            """ Initialize flags
            """
            self._flags = flags
            if solved is None:
                self._data = self.solveFlags(flags)
            else:
                self._data = solved

        def solveFlags(self, flags):
            """ Solve flags from given number data

            >>> f = MMU.Flags()
            >>> r = f.solveFlags(0x1)
            >>> f
            execute=False,ok=False,size=4,size1=False,size2=False,subtable=True,userspace=False,write=False
            >>> r = f.solveFlags(0x2)
            >>> f
            execute=True,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x4)
            >>> f
            execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=True
            >>> r = f.solveFlags(0x8)
            >>> f
            execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=True,write=False
            >>> r = f.solveFlags(0x10)
            >>> f
            execute=False,ok=False,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x20)
            >>> f
            execute=False,ok=False,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x30)
            >>> f
            execute=False,ok=False,size=65536,size1=True,size2=True,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x40)
            >>> f
            execute=False,ok=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0xFF)
            >>> f
            execute=True,ok=False,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True
            >>> r = f.solveFlags(0x1FF)
            >>> f
            execute=True,ok=True,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True
            """
            data = {
                'subtable': False,
                'execute': False,
                'write': False,
                'userspace': False,
                'size': 0,
                'size1': False,
                'size2': False,
                'ok': False,
                }
            if flags & 0x1 == 0x1:
                data['subtable'] = True
            if flags & 0x2 == 0x2:
                data['execute'] = True
            if flags & 0x4 == 0x4:
                data['write'] = True
            if flags & 0x8 == 0x8:
                data['userspace'] = True
            if flags & 0x10 == 0x10:
                data['size1'] = True
            if flags & 0x20 == 0x20:
                data['size2'] = True
            if flags & 0x100 == 0x100:
                data['ok'] = True

            # Determine page size in kilobytes
            if not data['size1'] and not data['size2']:
                data['size'] = 4
            elif data['size1'] and not data['size2']:
                data['size'] = 64
            elif not data['size1'] and data['size2']:
                data['size'] = 1024
            elif data['size1'] and data['size2']:
                data['size'] = 1024 * 64

            self._data = data
            return data

        def isSet(self, name):
            """ Checks whether element is set, or get value

            >>> f = MMU.Flags(0x1F)
            >>> f.isSet('size')
            64
            >>> f.isSet('size1')
            True
            >>> f.isSet('size2')
            False
            >>> f.isSet('subtable')
            True
            """
            if not name in self._data:
                return False

            return self._data[name]
    
        def __getitem__(self, name):
            if not name in self._data:
                return None

            return self._data[name]

        def dump(self):
            """ Dumps the flag status
            """
            return self._data

        def __repr__(self):
            """ Get string representation of the flags
            """
            #return "%s" % self.dump()
            a = self._data.keys()
            res = ''
            for k in sorted(a):
                if res:
                    res += ','
                res += '%s=%s' % (k, self._data[k])
            return res

"""
MMU

Initial table
"""
