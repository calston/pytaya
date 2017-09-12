import zlib, json

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory, connectWS

from twisted.internet.defer import Deferred, inlineCallbacks

class ScopeGenProProtocol(WebSocketClientProtocol):

    def __init__(self, *a, **kw):
        WebSocketClientProtocol.__init__(self, *a, **kw)

        self.params = {
            "in_command": {"value": "send_all_params"}
        }

    @inlineCallbacks
    def onOpen(self):
        yield self.sendMessage(json.dumps({"parameters": self.params}))

    def streamRecv(self, signals):
        pass

    def onMessage(self, payload, isBinary):
        if isBinary:
            q = payload
            try:
                t = zlib.decompress(q, 31)
                t = json.loads(t)
                params = t.get("parameters")
                if params:
                    if not self.params:
                        # We need to be able to merge our desired defaults
                        # on first connect. XXX Add this later XXX
                        pass
                    for q, v in params.items():
                        self.params[q] = v

                signals = t.get('signals')
                if signals:
                    self.streamRecv(signals)

            except Exception as e:
                # Yeah this is pretty horrible
                pass
