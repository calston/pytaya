
from __future__ import print_function

from twisted.internet import task
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver


class PitayaClient(LineReceiver):
    MAX_LENGTH = 134217728

    def connectionMade(self):
        self.commandQueue = []
        self.waiting = False
        self.received = []
        self.factory.connectPipe(self)

    @inlineCallbacks
    def sendLine(self, line, wait=False):
        if self.waiting:
            if wait:
                yield self.waiting
                mine = yield self.sendLine(line, wait=wait)
                returnValue(mine)
            else:
                self.commandQueue.append(line)
                returnValue(None)
        else:
            if wait:
                self.waiting = Deferred()
            
                t_ = yield LineReceiver.sendLine(self, line)

                return_line = yield self.waiting
                self.waiting = False
                returnValue(return_line)
            else:
                t_ = yield LineReceiver.sendLine(self, line)
                returnValue(t_)

    def lineReceived(self, line):
        if self.waiting:
            self.waiting.callback(line)
            while self.commandQueue:
                line = self.commandQueue.pop(0)
                LineReceiver.sendLine(self, line)
        else:
            self.received.append(line)

    def disconnect(self):
        self.transport.loseConnection()

class PitayaClientFactory(ClientFactory):
    protocol = PitayaClient

    def __init__(self, parent):
        self.connected = Deferred()
        self.parent = parent
        self.pipe = None

    def connectPipe(self, protocol):
        self.pipe = protocol
        self.connected.callback(protocol)

    def clientConnectionFailed(self, connector, reason):
        self.connected.errback(reason)
        self.connected = Deferred()

    def clientConnectionLost(self, connector, reason):
        self.pipe = None
        self.parent.pipe = None
        print('connection lost:', reason.getErrorMessage())
