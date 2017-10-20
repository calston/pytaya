#!/usr/bin/env python
import zlib, json

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor

from pytaya import RedPitaya
from pytaya.utils import wait


@inlineCallbacks
def sine(r):
    yield r.rf_out.quick_sine(1, 100000, 1.0)

@inlineCallbacks
def read_fast(r):
    yield r.rf_in.reset()
    yield r.rf_in.set_decimation(1)

    yield r.rf_in.set_trigger_level(0)
    yield r.rf_in.set_trigger_delay(0)
    yield r.rf_in.start()
    yield r.rf_in.set_trigger_pe(1)

    data = yield r.rf_in.get_trigger_data(1)

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
