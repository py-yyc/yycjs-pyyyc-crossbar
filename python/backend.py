from twisted.internet import defer

from autobahn.twisted.wamp import Session, ApplicationRunner
from autobahn.wamp.types import RegisterOptions, PublishOptions
from autobahn import wamp

import random
import itertools


class Client(object):
    """
    Represents a single client's board state.

    'name' is their session-id and 'color' is a randomly-assigned
    color 3-tuple
    """
    def __init__(self, name, color):
        self.name = name
        self.color = color
        # a 16x16 grid of False values
        self._state = []
        for y in range(16):
            self._state.append([False] * 16)

    def click(self, x, y):
        self._state[x][y] = not self._state[x][y]


class Board(object):
    """
    The state of the game board.

    Each client has a bool for each pixel; if it's true, their color
    contributes to the total for that board square.
    """
    def __init__(self):
        # client_id -> Client instance
        self._clients = {}
        self._color_generator = itertools.cycle(
            [
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
            ]
        )

    def click(self, client_id, x, y):
        self._clients[client_id].click(x, y)

    def client_add(self, client_id):
        color = next(self._color_generator)
        self._clients[client_id] = Client(client_id, color)

    def client_del(self, client_id):
        del self._clients[client_id]

    @wamp.register(u"meejah.get_client_count")
    def client_count(self):
        return len(self._clients)

    def _get_pixel(self, x, y):
        value = (0, 0, 0)
        for client in self._clients.values():
            if client._state[x][y]:
                value = (
                    max(value[0], client.color[0]),
                    max(value[1], client.color[1]),
                    max(value[2], client.color[2]),
                )
        return value

    @wamp.register(u"meejah.get_board")
    def as_json(self):
        # obviously, caching this would be a great idea...
        state = []
        for x in range(16):
            column = []
            for y in range(16):
                column.append(self._get_pixel(x, y))
            state.append(column)
        return state


class Game(Session):
    @defer.inlineCallbacks
    def on_join(self, details):
        self._board = Board()
        yield self.register(
            self._click, u"meejah.click",
            options=RegisterOptions(details_arg="details"),
        )
        yield self.register(self._board)
        yield self.subscribe(self)
        
    def on_leave(self, details):
        self.disconnect()

    @wamp.subscribe(u"wamp.session.on_leave")
    def _session_left(self, session):
        self._board.client_del(session)
        return self.publish(u"meejah.board_invalid")

    @wamp.subscribe(u"wamp.session.on_join")
    def _session_join(self, details):
        self._board.client_add(details['session'])
        return self.publish(u"meejah.board_invalid")

    @defer.inlineCallbacks
    def _click(self, x, y, details=None):
        """
        Public API, registerd as 'meejah.click'
        """
        self._board.click(details.caller, x, y)
        yield self.publish(
            u"meejah.board_update", x, y, self._board._get_pixel(x, y),
            options=PublishOptions(exclude_me=False),
        )


if __name__ == '__main__':
    runner = ApplicationRunner(u'ws://localhost:9999/ws', u'demo')
    # runner = ApplicationRunner(u'ws://yycjs.meejah.ca:9999/ws', u'demo')
    runner.run(Game)
