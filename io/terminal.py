
class Terminal:
    def __init__(self):
        self.screen = []
        self.width = 80
        self.height = 24
        self.base = 0
        self.resize()

    def setBase(self, base):
        self.base = base

    def resize(self):
        newsize = self.width*self.height
        if len(self.screen) >= newsize:
            self.screen = self.screen[:newsize]
        else:
            self.screen = [0]*(newsize)

    def setControl(self, pos, data):
        if data & 0xFF == 0xAA:
            self.width = data >> 8
            self.resize()
        if data & 0xFF == 0xBB:
            self.height = data >> 8
            self.resize()
        if data & 0xFF == 0x01:
            self.printScreen()

    def setData(self, pos, data):
        pos -= self.base
        if pos < 0:
            return
        if pos < len(self.screen):
            self.screen[pos] = data

    def getData(self, pos):
        if pos >=0 and pos < len(self.screen):
            return self.screen[pos]
        return None

    def getScreen(self):
        return self.screen

    def printScreen(self):
        print "==== screen ===="
        tmp = self.screen
        while tmp:
            line = tmp[:self.width]
            tmp = tmp[self.width:]
            s = ''.join([chr(i) for i in line])
            s = s.replace('\x00',' ')
            print s
        print "================"
