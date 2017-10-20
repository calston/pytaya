#!/usr/bin/env python
import zlib, json

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor

from pytaya import RedPitaya
from pytaya.utils import wait


@inlineCallbacks
def sine(r):
    yield r.send(b"GEN:RST")
    yield r.send(b"SOUR1:FUNC SINE")
    yield r.send(b"SOUR1:FREQ:FIX 100000")
    yield r.send(b"SOUR1:VOLT 1")
    yield r.send(b"OUTPUT1:STATE ON")

@inlineCallbacks
def read_fast(r):
    yield r.send("ACQ:RST")
    yield r.send("ACQ:DEC 1")
    yield r.send("ACQ:TRIG:LEV 0")
    yield r.send("ACQ:TRIG:DLY 0")
    yield r.send("ACQ:START")
    yield r.send("ACQ:TRIG CH1_PE")

    while 1:
        response = yield r.send("ACQ:TRIG:STAT?", wait=True)
        print response
        if response == "TD":
            break

    print "Acquiring"
    data = yield r.send("ACQ:SOUR1:DATA?", wait=True)

    print data

@inlineCallbacks
def startup():
    r = RedPitaya('192.168.200.50', 5000)
    yield r.connect()

    yield sine(r)

    yield read_fast(r)

if __name__ == '__main__':
    import sys
    from twisted.python import log

    log.startLogging(sys.stdout)

    reactor.callWhenRunning(startup)

    reactor.run()
