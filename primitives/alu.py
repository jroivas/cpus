
class ALU:
    """ The most simple Arithemetic unit
    """
    def add(self, *args):
        """ Add numbers together

        >>> a = ALU()
        >>> print a.add(1, 2)
        3
        >>> print a.add(1, 1)
        2
        >>> print a.add(1.6, 1.0)
        2.6
        >>> print a.add(-1, 2)
        1
        >>> print a.add(-1, -1)
        -2
        """
        res = 0
        for item in args:
            res += item
        return res

    def sub(self, *args):
        """ Subtract numbers

        >>> a = ALU()
        >>> print a.sub(2, 1)
        1
        >>> print a.sub(1, 1)
        0
        >>> print a.sub(1.6, 1.0)
        0.6
        >>> print a.sub(-1, 2)
        -3
        >>> print a.sub(-1, -1)
        0
        >>> print a.sub(8, 5)
        3
        >>> print a.sub()
        0
        >>> print a.sub(1)
        1
        >>> print a.sub(8, 5, 2)
        1
        """
        if not args:
            return 0
        res = args[0]
        for item in args[1:]:
            res -= item
        return res

    def mul(self, *args):
        """ Multiple numbers together

        >>> a = ALU()
        >>> print a.mul(1, 2)
        2
        >>> print a.mul(1, 2, 3)
        6
        >>> print a.mul(1.5, 2)
        3.0
        """
        if not args:
            return 0
        res = args[0]
        for item in args[1:]:
            res *= item
        return res

    def div(self, *args):
        """ Divide first argument with others

        >>> a = ALU()
        >>> print a.div(1, 2)
        0
        >>> print a.div(1, 2.0)
        0.5
        >>> print a.div(6, 2)
        3
        >>> print a.div(12, 2, 3)
        2
        """
        res = args[0]
        for item in args[1:]:
            res /= item
        return res

    def mod(self, *args):
        """ Take remainder of integer dividation

        >>> a = ALU()
        >>> print a.mod(1, 2)
        1
        >>> print a.mod(7, 3)
        1
        >>> print a.mod(8, 3)
        2
        >>> print a.mod(9, 3)
        0
        >>> print a.mod(25, 11)
        3
        >>> print a.mod(26, 11, 3)
        1
        """
        res = args[0]
        for item in args[1:]:
            res %= item
        return res

    def b_shl(self, r1, r2):
        """ Shift left

        >>> a = ALU()
        >>> a.b_shl(1, 1)
        2
        >>> a.b_shl(1, 2)
        4
        >>> a.b_shl(3, 1)
        6
        """
        return r1 << r2

    def b_shr(self, r1, r2):
        """ Shift right

        >>> a = ALU()
        >>> a.b_shr(2, 1)
        1
        >>> a.b_shr(4, 1)
        2
        >>> a.b_shr(10, 1)
        5
        >>> a.b_shr(10, 2)
        2
        """
        return r1 >> r2

    def b_and(self, r1, r2):
        """ Bitwise and

        >>> a = ALU()
        >>> a.b_and(1, 1)
        1
        >>> a.b_and(2, 1)
        0
        >>> a.b_and(3, 1)
        1
        >>> a.b_and(0xFF, 3)
        3
        >>> a.b_and(5, 4)
        4
        >>> a.b_and(7, 5)
        5
        """
        return r1 & r2

    def b_or(self, r1, r2):
        """ Bitwise or

        >>> a = ALU()
        >>> a.b_or(1, 1)
        1
        >>> a.b_or(1, 0)
        1
        >>> a.b_or(0, 1)
        1
        >>> a.b_or(0, 0)
        0
        >>> a.b_or(3, 1)
        3
        >>> a.b_or(2, 1)
        3
        """
        return r1 | r2

    def b_xor(self, r1, r2):
        """ Bitwise exclusive or

        >>> a = ALU()
        >>> a.b_xor(1, 1)
        0
        >>> a.b_xor(1, 0)
        1
        >>> a.b_xor(0, 1)
        1
        >>> a.b_xor(0, 0)
        0
        >>> a.b_xor(3, 1)
        2
        >>> a.b_xor(2, 1)
        3
        """
        return r1 ^ r2

    def b_not(self, r):
        """ Bitwise not

        >>> a = ALU()
        >>> print '%x' % (a.b_not(1) & 0xff)
        fe
        >>> print '%x' % (a.b_not(0xa) & 0xff)
        f5
        >>> print '%x' % (a.b_not(0xf8) & 0xff)
        7
        """
        return ~ r

    def forceInt(self, r):
        """ Force number to be integer
        
        >>> a = ALU()
        >>> print a.forceInt(5.0)
        5
        >>> print a.forceInt(4.2)
        4
        >>> print a.forceInt(1.2e-5)
        0
        """
        return int(r)
