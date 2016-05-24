from twisted.internet import defer

from autobahn.twisted.wamp import Session, ApplicationRunner
from autobahn.twisted.util import sleep
import random

class RandomAgent(Session):
    @defer.inlineCallbacks
    def on_join(self, details):
        while True:
            x = yield self.call(
                u"meejah.click",
                random.randint(0, 15),
                random.randint(0, 15),
            )
            print(x)
            yield sleep(.5)


if __name__ == '__main__':
    # runner = ApplicationRunner(u'ws://localhost:9999/ws', u'demo')
    runner = ApplicationRunner(u'ws://pyyyc.meejah.ca/ws', u'demo')
    runner.run(RandomAgent)
