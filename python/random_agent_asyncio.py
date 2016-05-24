from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import random
import asyncio

class RandomAgent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        while True:
            yield from self.call(
                u"meejah.click",
                random.randint(0, 15),
                random.randint(0, 15),
            )
            yield from asyncio.sleep(.5)


if __name__ == '__main__':
    #runner = ApplicationRunner(u'ws://localhost:9999/ws', u'demo')
    runner = ApplicationRunner(u'ws://pyyyc.meejah.ca/ws', u'demo')
    runner.run(RandomAgent)
