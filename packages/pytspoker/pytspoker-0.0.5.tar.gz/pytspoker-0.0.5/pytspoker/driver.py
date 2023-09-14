import os
import sys
import traceback
import weakref
import importlib
class DriverProxy(object):
    def __init__(self, engine, driverName, debug):
        if driverName is None:
            # pick default drivers for common platforms
            if sys.platform == 'darwin':
                driverName = 'nsss'
            elif sys.platform == 'win32':
                driverName = 'sapi5'
            else:
                driverName = 'espeak'
        name = 'pytspoker.drivers.%s' % driverName
        self._module = importlib.import_module(name)
        # build drivers instance
        self._driver = self._module.buildDriver(weakref.proxy(self))
        # initialize refs
        self._engine = engine
        self._queue = []
        self._busy = True
        self._name = None
        self._iterator = None
        self._debug = debug

    def __del__(self):
        try:
            self._driver.destroy()
        except (AttributeError, TypeError):
            pass

    def _push(self, mtd, args, name=None):
        self._queue.append((mtd, args, name))
        self._pump()

    def _pump(self):
        while (not self._busy) and len(self._queue):
            cmd = self._queue.pop(0)
            self._name = cmd[2]
            try:
                cmd[0](*cmd[1])
            except Exception as e:
                self.notify('error', exception=e)
                if self._debug:
                    traceback.print_exc()

    def notify(self, topic, **kwargs):
        kwargs['name'] = self._name
        self._engine._notify(topic, **kwargs)

    def setBusy(self, busy):
        self._busy = busy
        if not self._busy:
            self._pump()

    def isBusy(self):
        return self._busy

    def say(self, text, name):
        self._push(self._driver.say, (text,), name)

    def stop(self):

        while(True):
            try:
                mtd, args, name = self._queue[0]
            except IndexError:
                break
            if(mtd == self._engine.endLoop):
                break
            self._queue.pop(0)
        self._driver.stop()

    def save_to_file(self, text, filename, name):
        self._push(self._driver.save_to_file, (text, filename), name)
    def join_file(self, filename, name):
        return os.path.join(filename, name)

    def getProperty(self, name):
        return self._driver.getProperty(name)

    def setProperty(self, name, value):
        self._push(self._driver.setProperty, (name, value))

    def runAndWait(self):
        self._push(self._engine.endLoop, tuple())
        self._driver.startLoop()

    def startLoop(self, useDriverLoop):
        if useDriverLoop:
            self._driver.startLoop()
        else:
            self._iterator = self._driver.iterate()
    def endLoop(self, useDriverLoop):
        self._queue = []
        self._driver.stop()
        if useDriverLoop:
            self._driver.endLoop()
        else:
            self._iterator = None
        self.setBusy(True)
    def iterate(self):
        try:
            next(self._iterator)
        except StopIteration:
            pass