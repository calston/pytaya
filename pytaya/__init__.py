from twisted.internet.defer import Deferred, inlineCallbacks, returnValue, waitForDeferred
from twisted.internet.error import ConnectionRefusedError
from twisted.internet import reactor
from twisted.python import log

from pytaya.protocol import PitayaClientFactory, PitayaClient
from pytaya.utils import HTTPRequest, wait

from pytaya.functions import OutputRF, InputRF


class RedPitaya(object):
    def __init__(self, ip, port=5000):
        self.ip = ip
        self.port = port
        self.factory = None
        self.pipe = None

        self.connecting = False
        self.reconnecting = False
        self.started = False

        self.rf_out = OutputRF(self)
        self.rf_in = InputRF(self)

    @inlineCallbacks
    def startApp(self):
        try:
            e = yield HTTPRequest.get('http://%s/start_scpi_manager' % (self.ip))
            returnValue(e.startswith('OK'))
        except Exception as e:
            print("Connection error %s" % str(e))
            returnValue(False)

    @inlineCallbacks
    def stopApp(self):
        try:
            e = yield HTTPRequest.get('http://%s/stop_scpi_manager' % (self.ip))
            returnValue(e.startswith('OK'))
        except Exception as e:
            print("Connection error %s" % str(e))
            returnValue(False)

    @inlineCallbacks
    def send(self, cmd, wait=False):
        pipe = yield self.getConnection()
        yield pipe.sendLine(cmd, wait=wait)

    @inlineCallbacks
    def getConnection(self):
        if self.connecting:
            log.msg("Waiting for connection")
            while not self.pipe:
                yield wait(10)
            defer.returnValue(self.pipe)

        if not self.factory:
            log.msg("Starting remote SCPI application")
            self.connecting = True

            self.started = True
            while not self.started:
                self.started = yield self.startApp()
                if not self.started:
                    yield wait(10)

            self.factory = PitayaClientFactory(self)

        while not self.pipe:
            self.connecting = True
            log.msg("Connecting SCPI")
            try:
                yield reactor.connectTCP(self.ip, self.port, self.factory)
                try:
                    self.pipe = yield self.factory.connected
                    self.connecting = False
                except Exception as e:
                    pass
            except ConnectionRefusedError as e:
                log.msg("Retrying in 1s...")

            yield wait(1000)

        returnValue(self.pipe)

    def shutdown(self):
        log.msg('Shutting down')
        return self.stopApp()
