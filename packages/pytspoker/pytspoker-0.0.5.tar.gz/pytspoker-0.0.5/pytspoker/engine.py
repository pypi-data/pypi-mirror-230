from . import driver
import traceback
import weakref



class Engine(object):

    def __init__(self, driverName=None, debug=False):
        self.proxy = driver.DriverProxy(weakref.proxy(self), driverName, debug)
        self._connects = {}
        self._inLoop = False
        self._driverLoop = True
        self._debug = debug

    def _notify(self, topic, **kwargs):
        for cb in self._connects.get(topic, []):
            try:
                cb(**kwargs)
            except Exception:
                if self._debug:
                    traceback.print_exc()

    def connect(self, topic, cb):
        arr = self._connects.setdefault(topic, [])
        arr.append(cb)
        return {'topic': topic, 'cb': cb}

    def disconnect(self, token):
        topic = token['topic']
        try:
            arr = self._connects[topic]
        except KeyError:
            return
        arr.remove(token['cb'])
        if len(arr) == 0:
            del self._connects[topic]
    def check_connect(self, check):
        if check:
            return "Connected successfully"
        else:
            return "There is a connection problem, try again"



    def say(self, text, name=None):
        if text == None:
            return "Argument value can't be none or empty"
        else:
            self.proxy.say(text, name)

    def stop(self):
        self.proxy.stop()
    def destroy(self):
        self.proxy.stop()
        self.proxy.isBusy()
    def resume(self, text, name=None):
        if self.proxy.say(text, name):
            return "Text is being converted"
        else:
            self.proxy.say(text, name)
    def save_to_file(self, text, filename, name=None):
        self.proxy.save_to_file(text, filename, name)

    def isBusy(self):
        return self.proxy.isBusy()

    def getProperty(self, name):
        return self.proxy.getProperty(name)

    def setProperty(self, name, value):
        self.proxy.setProperty(name, value)

    def runAndWait(self):
        if self._inLoop:
            raise RuntimeError('run loop already started')
        self._inLoop = True
        self._driverLoop = True
        self.proxy.runAndWait()

    def startLoop(self, useDriverLoop=True):
        if self._inLoop:
            raise RuntimeError('run loop already started')
        self._inLoop = True
        self._driverLoop = useDriverLoop
        self.proxy.startLoop(self._driverLoop)

    def endLoop(self):
        if not self._inLoop:
            raise RuntimeError('run loop not started')
        self.proxy.endLoop(self._driverLoop)
        self._inLoop = False

    def iterate(self):
        if not self._inLoop:
            raise RuntimeError('run loop not started')
        elif self._driverLoop:
            raise RuntimeError('iterate not valid in drivers run loop')
        self.proxy.iterate()