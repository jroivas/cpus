
class ALU:
    """ The most simple Arithemetic unit
    """
    def __init__(self):
        self.state = None

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
        """ Subtract two numbers

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
        """
        if not args:
            return 0
        res = args[0]
        for item in args[1:]:
            res -= item
        return res

    def mul(self, *args):
        """
        >>> a = ALU()
        >>> print a.mul(1, 2)
        2
        >>> print a.mul(1, 2, 3)
        6
        >>> print a.mul(1.5, 2)
        3.0
        """
        res = args[0]
        for item in args[1:]:
            res *= item
        return res

    def div(self, *args):
        """
        >>> a = ALU()
        >>> print a.div(1, 2)
        0
        >>> print a.div(1, 2.0)
        0.5
        >>> print a.div(6, 2)
        3
        """
        res = args[0]
        for item in args[1:]:
            res /= item
        return res

    def mod(self, r1, r2):
        return r1 % r2

    def b_shl(self, r1, r2):
        return r1 << r2

    def b_shr(self, r1, r2):
        return r1 >> r2

    def b_and(self, r1, r2):
        return r1 & r2

    def b_or(self, r1, r2):
        return r1 | r2

    def b_xor(self, r1, r2):
        return r1 ^ r2

    def b_not(self, r):
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

    def getState(self):
        return self.state
