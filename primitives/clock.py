from threading import Timer

class Clock:
    def __init__(self, hz=100, callfunc=None, params=None):
        """ Initialize the timer
        """
        self.callfunc = callfunc
        self.params = params
        self.hz = hz
        if self.hz == 0:
            self.hz = 100
        self.timer = None
        #self.timer = Timer(100.0/self.hz, self.run)
        self.enabled = False

    def start(self):
        """ Start the timer

        >>> def tmp(pars):
        ...   print pars
        >>> import time
        >>> t = Clock(1000, tmp, 42)
        >>> t.start()
        >>> time.sleep(0.5) #doctest: +ELLIPSIS
        42...
        >>> t.stop()
        """
        self.enabled = True
        self.timer = Timer(100.0/self.hz, self.run)
        self.timer.start()

    def pause(self):
        """ Temporarily pause the timer
        """
        self.enabled = False

    def unpause(self):
        """ Continue paused timer
        """
        self.enabled = True

    def stop(self):
        """ Stop the timer
        """
        self.callfunc = None
        self.enabled = False

    def run(self):
        """ On timer hit run callback function
        >>> def tmp_list(*pars):
        ...   print pars
        >>> def tmp_dict(**pars):
        ...   print pars
        >>> import time
        >>> t = Clock(1000, tmp_list, [1,2])
        >>> t.start()
        >>> time.sleep(0.5) #doctest: +ELLIPSIS
        (1, 2)...
        >>> t.stop()
        >>> t = Clock(1000, tmp_dict, {'test': 42, 'val': 5})
        >>> t.start()
        >>> time.sleep(0.5) #doctest: +ELLIPSIS
        {'test': 42, 'val': 5}...
        >>> t.stop()
        """
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
