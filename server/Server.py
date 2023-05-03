from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import pickle
from Query import Query
from Session import Session
from config import field_size


class BattleshipProtocol(LineReceiver):
    def __init__(self, users, protocols):
        self.users = users
        self.username = None
        self.protocols = protocols
        self.session = None
        self.pair = None
        self.user = None

    def send_query(self, type, data=None):
        print('Sending', type)
        self.sendLine(pickle.dumps(Query(type, data)))

    def connectionMade(self):
        self.send_query('choose_mode')

    def connectionLost(self, reason):
        if self.username in self.users:
            self.users.remove(self.username)
        if self.username in self.protocols.keys():
            del self.protocols[self.username]
        if self.pair is not None:
            self.pair.transport.loseConnection()

    def lineReceived(self, data):
        query = pickle.loads(data)
        print('Data received:')
        print(query.type)
        print(query.data)
        if query.type == 'set_username':
            self.handle_username(query.data)
        elif query.type == 'update_player_list':
            self.choose_player()
        elif query.type == 'chose_opponent':
            self.handle_chose_opponent(query.data)
        elif query.type == 'set_mode_waiting':
            self.handle_set_mode_waiting()
        elif query.type == 'set_mode_choosing':
            self.handle_set_mode_choosing()
        elif query.type == 'set_ship_place':
            self.handle_set_ship_place(query.data)
        elif query.type == 'set_shot_coordinate':
            self.handle_set_shot_coordinate(query.data)

    def handle_username(self, username):
        if username in self.users:
            self.send_query('incorrect_username')
        else:
            self.username = username
            self.users.add(self.username)
            self.protocols[self.username] = self

    def choose_mode(self):
        self.send_query('choose_mode')

    def handle_set_mode_waiting(self):
        self.send_query('get_username')

    def handle_set_mode_choosing(self):
        self.choose_player()

    def choose_player(self):
        other_players = self.users.copy()
        self.send_query('choose_player', other_players)

    def handle_chose_opponent(self, username):
        if username not in self.users:
            self.send_query('opponent_taken')
        else:
            self.users.remove(username)
            session = Session(field_size, self, self.protocols[username])
            self.session = session
            self.protocols[username].session = session
            self.pair = self.protocols[username]
            self.protocols[username].pair = self
            self.user = 0
            self.protocols[username].user = 1
            session.start()

    def handle_set_ship_place(self, placement):
        self.session.place_one_ship(self.user, placement)

    def handle_set_shot_coordinate(self, shot):
        self.session.set_shot_coordinate(shot, self.user)


class BattleshipFactory(Factory):
    def __init__(self):
        self.users = set()
        self.protocols = {}

    def buildProtocol(self, addr):
        return BattleshipProtocol(self.users, self.protocols)


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 8123)
    endpoint.listen(BattleshipFactory())
    reactor.run()
    