from twisted.internet import defer

from autobahn.twisted import wamp
from autobahn.twisted.util import sleep
import random

class DiagonalAgent(wamp.ApplicationSession):
    @defer.inlineCallbacks
    def onJoin(self, details):
        print("agent joined")
        while True:
            for x in range(16):
                yield self.call(u"meejah.click", x, x)
                yield sleep(0.5)


if __name__ == '__main__':
    runner = wamp.ApplicationRunner(u'ws://localhost:9999/ws', u'demo')
    runner.run(DiagonalAgent)
