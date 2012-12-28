from threading import Timer

class Clock:
    def __init__(self, hz=100, callfunc=None, params=None):
        self.callfunc = callfunc
        self.params = params
        self.hz = hz
        if self.hz == 0:
            self.hz = 100
        self.timer = Timer(100.0/self.hz, self.run)
        self.enabled = False

    def start(self):
        self.enabled = True
        self.timer = Timer(100.0/self.hz, self.run)
        self.timer.start()

    def stop(self):
        self.callfunc = None
        self.enabled = False

    def run(self):
        if self.callfunc is None:
            return
        if not self.enabled:
            self.start()
            return

        if self.params is None:
            self.callfunc()
        elif type(self.params) == dict:
            self.callfunc(**self.params)
        elif type(self.params) == list:
            self.callfunc(*self.params)
        else:
            self.callfunc(self.params)

        self.start()
