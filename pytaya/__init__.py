from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twisted.internet import reactor
from twisted.python import log

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory, connectWS

from pytaya.protocol import PitayaClientFactory, PitayaClient
from pytaya.utils import HTTPRequest


class RedPitaya(object):
    def __init__(self, ip, port=5000):
        self.ip = ip
        self.port = port
        self.factory = None
        self.pipe = None

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

    def send(self, cmd, wait=False):
        if not self.pipe:
            raise Exception("Not connected")
            
        return self.pipe.sendLine(cmd, wait=wait)

    @inlineCallbacks
    def connect(self):
        if not self.factory:
            started = yield self.startApp()

            if started:
                self.factory = PitayaClientFactory(self)

                reactor.connectTCP(self.ip, self.port, self.factory)

                self.pipe = yield self.factory.connected

    def shutdown(self):
        log.msg('Shutting down')
        return self.stopApp()
