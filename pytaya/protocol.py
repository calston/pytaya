
from __future__ import print_function

from twisted.internet import task
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver


class PitayaClient(LineReceiver):
    def connectionMade(self):
        print("Connected")
        self.factory.connectPipe(self)

    def signalGeneratorReset(self):
        self.sendLine(b"GEN:RST")

    def lineReceived(self, line):
        print("receive:", repr(line))

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
        print('connection failed:', reason.getErrorMessage())
        self.connected.errback(reason)

    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
