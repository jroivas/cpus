class MMU:
    class Flags:
        def __init__(self, flags=0):
            """ Initialize flags
            """
            self._flags = flags
            self._solved_flags = self.solveFlags(flags)

        def solveFlags(self, flags):
            """ Solve flags from given number data

            >>> f = MMU.Flags()
            >>> r = f.solveFlags(0x1)
            >>> f
            execute=False,size=4,size1=False,size2=False,subtable=True,userspace=False,write=False
            >>> r = f.solveFlags(0x2)
            >>> f
            execute=True,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x4)
            >>> f
            execute=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=True
            >>> r = f.solveFlags(0x8)
            >>> f
            execute=False,size=4,size1=False,size2=False,subtable=False,userspace=True,write=False
            >>> r = f.solveFlags(0x10)
            >>> f
            execute=False,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x20)
            >>> f
            execute=False,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x30)
            >>> f
            execute=False,size=65536,size1=True,size2=True,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0x40)
            >>> f
            execute=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False
            >>> r = f.solveFlags(0xFF)
            >>> f
            execute=True,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True
            """
            data = {
                'subtable': False,
                'execute': False,
                'write': False,
                'userspace': False,
                'size': 0,
                'size1': False,
                'size2': False,
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

            # Determine page size in kilobytes
            if not data['size1'] and not data['size2']:
                data['size'] = 4
            elif data['size1'] and not data['size2']:
                data['size'] = 64
            elif not data['size1'] and data['size2']:
                data['size'] = 1024
            elif data['size1'] and data['size2']:
                data['size'] = 1024*64

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
            if not name in self._solved_flags:
                return False

            return self._solved_flags[name]

        def dump(self):
            """ Dumps the flag status
            """
            return self._data

        def __repr__(self):
            """ Get string representation of the flags
            """
            a = self._data.keys()
            res = ''
            for k in sorted(a):
                if res:
                    res += ','
                res += '%s=%s' % (k, self._data[k])
            return res

    def __init__(self, mem):
        """ Initialize MMU
        """
        self._enabled = False
        self._mem = mem
        self._wordsize = 4

    def getEntries(self, entries):
        """ Get page entries and parse them, handle recursively
        """
        subs = []
        for (addr, flags) in entries:
            if flags.isSet('subtable'):
                size = flags.isSet('size') * 1024 / 4
                if size > 0:
                    tmp = self.readTable(addr, size)
                    subs += self.getEntries(tmp)
            else:
                if addr > 0:
                    subs.append((addr, flags))
        return subs

    def initialize(self, tablepos, tablesize):
        """ Initializes MMU with a initial page
        Does recursive parsing

        >>> from primitives import Mem
        >>> m = Mem(1024*100)
        >>> # Subtable, starts at 4k
        >>> m.setData(10, 0x00001011, 4)
        >>> # Page, starts at 32k, size 64k
        >>> m.setData(14, 0x00008010, 4)
        >>> for i in xrange(1023):
        ...   m.setData(0x1000 + i, 0)
        >>> # Page at 8k, size 4k
        >>> m.setData(0x1000, 0x00002000, 4)
        >>> # Page at 12k, size 1M 
        >>> m.setData(0x1004, 0x00003020, 4)
        >>> u = MMU(m)
        >>> u.initialize(10, 3)
        [(8192, execute=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False), (12288, execute=False,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False), (32768, execute=False,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False)]
        """
        entries = self.readTable(tablepos, tablesize)
        self._table = self.getEntries(entries)
        return self._table

    def readTable(self, tablepos, tablesize):
        """ Reads table from memory

        >>> from primitives import Mem
        >>> m = Mem(1024*32)
        >>> # Subtable, starts at 4k
        >>> m.setData(10, 0x00001011, 4)
        >>> # Page, starts at 32k, size 64k
        >>> m.setData(14, 0x00008010, 4)
        >>> for i in xrange(1023):
        ...   m.setData(0x1000 + i, 0)
        >>> u = MMU(m)
        >>> tmp = u.readTable(10, 3)
        >>> tmp[0][0]
        4096
        >>> tmp[1][0]
        32768
        >>> tmp[2][0]
        0
        >>> tmp[0][1]
        execute=False,size=64,size1=True,size2=False,subtable=True,userspace=False,write=False
        >>> tmp[1][1]
        execute=False,size=64,size1=True,size2=False,subtable=False,userspace=False,write=False
        >>> tmp[2][1]
        execute=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False
        """
        datas = []
        for index in xrange(tablesize):
            tmp = self._mem.getData(tablepos + index*4, self._wordsize)
            datas.append(self.readEntry(tmp))

        return datas

    def readEntry(self, data):
        """ Read entry from one page table item data

        >>> from primitives import Mem
        >>> m = Mem()
        >>> u = MMU(m)
        >>> u.readEntry(0x00001000)
        (4096, execute=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False)
        >>> u.readEntry(0x00001111)
        (4096, execute=False,size=64,size1=True,size2=False,subtable=True,userspace=False,write=False)
        >>> u.readEntry(0x00001022)
        (4096, execute=True,size=1024,size1=False,size2=True,subtable=False,userspace=False,write=False)
        >>> u.readEntry(0x00002FFF)
        (8192, execute=True,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True)
        >>> u.readEntry(0xFFFFFFFF)
        (4294963200, execute=True,size=65536,size1=True,size2=True,subtable=True,userspace=True,write=True)
        >>> u.readEntry(0)
        (0, execute=False,size=4,size1=False,size2=False,subtable=False,userspace=False,write=False)
        """
        flags = MMU.Flags(data & 0xFFF)
        addr = data & 0xFFFFF000

        return (addr, flags)

"""
MMU

Initial table
"""
