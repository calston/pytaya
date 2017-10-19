#!/usr/bin/env python
import zlib, json

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor

from pytaya import RedPitaya


@inlineCallbacks
def startup():
    r = RedPitaya('192.168.200.50', 5000)
    yield r.connect()

    yield r.send(b"GEN:RST")
    yield r.send(b"SOUR1:FUNC SINE")
    yield r.send(b"SOUR1:FREQ:FIX 100000")
    yield r.send(b"SOUR1:VOLT 1")
    yield r.send(b"OUTPUT1:STATE ON")

if __name__ == '__main__':
    import sys
    from twisted.python import log

    log.startLogging(sys.stdout)

    reactor.callWhenRunning(startup)

    reactor.run()
