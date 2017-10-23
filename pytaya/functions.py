import time
import json

from twisted.internet.defer import inlineCallbacks, returnValue

from pytaya.utils import wait


class Function(object):
    def __init__(self, parent):
        self.r = parent

class OutputRF(Function):
    @inlineCallbacks
    def quick_sine(self, channel, frequency, amplitude):
        yield self.reset()

        yield self.set_function(channel, 'sine')
        yield self.set_amplitude(channel, amplitude)
        yield self.set_frequency(channel, frequency)

        yield self.output_enable(channel)

    def set_amplitude(self, channel, amplitude):
        return self.r.send(b"SOUR%s:VOLT %f" % (channel, float(amplitude)))

    def set_frequency(self, channel, frequency):
        return self.r.send(b"SOUR%s:FREQ:FIX %s" % (channel, frequency))

    def set_function(self, channel, func):
        return self.r.send(b"SOUR%s:FUNC %s" % (channel, func.upper()))

    def reset(self):
        return self.r.send(b"GEN:RST")

    def output_enable(self, channel):
        return self.r.send(b"OUTPUT%s:STATE ON" % channel)
     
    def output_disable(self, channel):
        return self.r.send(b"OUTPUT%s:STATE OFF" % channel)

class InputRF(Function):
    trigger_sources = [
        "DISABLED", "NOW", "CH1_PE", "CH1_NE", "CH2_PE", "CH2_NE", "EXT_PE",
        "EXT_NE", "AWG_PE", "AWG_NE"
    ]

    @inlineCallbacks
    def wait_trigger(self, response="TD", timeout=10):
        st = time.time()
	while 1:
	    res = yield self.r.send("ACQ:TRIG:STAT?", wait=True)

	    if res == response:
                returnValue(True)

            if (time.time() - st) > timeout:
                returnValue(None)

            yield wait(100)

    @inlineCallbacks
    def get_trigger_data(self, channel, timeout=10):

        trig = yield self.wait_trigger(timeout=timeout)

        if trig:
            data = yield self.get_channel_data(channel)
            data = data.strip()[1:-1]

            returnValue([float(v) for v in data.split(',')])

        returnValue(None)

    def get_channel_data(self, channel):
	return self.r.send("ACQ:SOUR%s:DATA?" % channel, wait=True)

    def reset(self):
        return self.r.send("ACQ:RST")

    def set_units(self, raw=True):
        return self.r.send("ACQ:GET:DATA:UNITS %s" % (
                                raw and "RAW" or "VOLTS"))

    def set_averaging(self, avg):
        return self.r.send("ACQ:AVG %s" % (avg and "ON" or "OFF"))

    def set_decimation(self, d):
        return self.r.send("ACQ:DEC %d" % d)

    def set_trigger_level(self, mv):
        return self.r.send("ACQ:TRIG:LEV %d" % mv)

    def set_trigger_delay(self, s):
        return self.r.send("ACQ:TRIG:DLY %d" % s)

    def set_trigger_delay_ns(self, t):
        return self.r.send("ACQ:TRIG:DLY:NS %d" % t)

    def set_trigger_pe(self, channel):
        return self.r.send("ACQ:TRIG CH%s_PE" % channel)

    def set_trigger_ne(self, channel):
        return self.r.send("ACQ:TRIG CH%s_NE" % channel)

    def set_trigger(self, trigger):
        if trigger in self.trigger_sources:
            return self.r.send("ACQ:TRIG %s" % trigger)
        else:
            raise Exception("Invalid trigger type %s, need one of %s" % (
                            trigger, ', '.join(self.trigger_sources)))

    def set_channel_gain(self, channel, hv):
        return self.r.send("ACQ:SOUR%s:GAIN %s" % (channel, hv and "HV" or "LV"))

    def start(self):
        return self.r.send("ACQ:START")

    def stop(self):
        return self.r.send("ACQ:STOP")

