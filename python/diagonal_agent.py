from twisted.internet import defer

from autobahn.twisted.wamp import Session, ApplicationRunner
from autobahn.twisted.util import sleep
import random

class DiagonalAgent(Session):
    @defer.inlineCallbacks
    def on_join(self, details):
        while True:
            for x in range(16):
                yield self.call(u"meejah.click", x, x)
                yield sleep(0.5)


if __name__ == '__main__':
    runner = ApplicationRunner(u'ws://localhost:9999/ws', u'demo')
    runner.run(DiagonalAgent)
