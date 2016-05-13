from twisted.internet import defer

from autobahn.twisted import wamp
from autobahn.twisted.util import sleep
import random

class RandomAgent(wamp.ApplicationSession):
    @defer.inlineCallbacks
    def onJoin(self, details):
        while True:
            yield self.call(
                u"meejah.click",
                random.randint(0, 15),
                random.randint(0, 15),
            )
            yield sleep(.5)


if __name__ == '__main__':
#    runner = wamp.ApplicationRunner(u'ws://localhost:9999/ws', u'demo')
    runner = wamp.ApplicationRunner(u'ws://yycjs.meejah.ca/ws', u'demo')
    runner.run(RandomAgent)
