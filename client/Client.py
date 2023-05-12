from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import pickle
from Query import Query
from Interfaces.VisualInterface import VisualInterface
from config import field_size, ip_address


def get_interface_type():
    return VisualInterface


class ClientProtocol(LineReceiver):
    def __init__(self):
        self.interface = None

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        if reactor.running:
            reactor.stop()

    def send_query(self, type, data=None):
        self.sendLine(pickle.dumps(Query(type, data)))

    def lineReceived(self, data):
        query = pickle.loads(data)
        # print('Data received')
        # print(query.type)
        # print(query.data)
        if query.type == 'get_username':
            self.handle_get_username()
        elif query.type == 'incorrect_username':
            self.handle_incorrect_username()
        elif query.type == 'choose_mode':
            self.handle_choose_mode()
        elif query.type == 'choose_player':
            self.handle_choose_player(query.data)
        elif query.type == 'opponent_taken':
            self.handle_opponent_taken()
        elif query.type == 'start_session':
            self.handle_start_session()
        elif query.type == 'end_session':
            self.handle_end_session(query.data)
        elif query.type == 'start_placing_ships':
            self.handle_start_placing_ships()
        elif query.type == 'get_ship_place':
            self.handle_get_ship_place(query.data)
        elif query.type == 'incorrect_ship_placement':
            self.handle_incorrect_ship_placement(*query.data)
        elif query.type == 'place_ship':
            self.handle_place_ship(query.data)
        elif query.type == 'wait_for_opponent':
            self.handle_wait_for_opponent()
        elif query.type == 'start_turn':
            self.handle_start_turn(query.data)
        elif query.type == 'get_shot_coordinate':
            self.handle_get_shot_coordinate()
        elif query.type == 'incorrect_shot':
            self.handle_incorrect_shot(query.data)
        elif query.type == 'set_miss':
            self.handle_set_miss(*query.data)
        elif query.type == 'set_shot':
            self.handle_set_shot(*query.data)
        elif query.type == 'set_sunk_ship':
            self.handle_set_sunk_ship(*query.data)
        elif query.type == 'end_turn':
            self.handle_end_turn(query.data)

    def handle_get_username(self):
        username = input('Set your username: ')
        self.send_query('set_username', username)

    def handle_incorrect_username(self):
        username = input('This username is already taken.\nSet another your username: ')
        self.send_query('set_username', username)

    def handle_choose_mode(self):
        print('Choose mode:')
        print('\"waiting\" - if you\'re gonna wait for opponent, or')
        print('\"choosing\" - if you\'re gonna choose opponent')
        result = input()
        while result != 'waiting' and result != 'choosing':
            print('Type \"waiting\" or \"choosing\"')
            result = input()
        if result == 'waiting':
            self.send_query('set_mode_waiting')
        elif result == 'choosing':
            self.send_query('set_mode_choosing')

    def handle_choose_player(self, players):
        print('Choose one of this players:')
        if len(players) == 0:
            print('No players available')
        else:
            for player in players:
                print(player)
        print('Or print \"update\" to update list of players')
        result = input()
        while result != 'update' and result not in players:
            print('You didn\'t choose one of players. Type again:')
            result = input()
        if result == 'update':
            self.send_query('update_player_list')
        else:
            self.send_query('chose_opponent', result)

    def handle_opponent_taken(self):
        print('Player is already playing or disconnected. Try again.')
        self.send_query('update_player_list')

    def handle_start_session(self):
        self.interface = get_interface_type()(field_size)
        self.interface.start_session()

    def handle_end_session(self, won):
        self.interface.end_session(won)

    def handle_start_placing_ships(self):
        self.interface.start_placing_ships()

    def handle_get_ship_place(self, type):
        placement = self.interface.get_ship_place(type)
        if placement[0] == (-1, -1):
            reactor.stop()
        else:
            self.send_query('set_ship_place', placement)

    def handle_incorrect_ship_placement(self, exc, first_square, second_square):
        self.interface.incorrect_ship_placement(exc, first_square, second_square)

    def handle_place_ship(self, ship):
        self.interface.place_ship(ship)

    def handle_wait_for_opponent(self):
        self.interface.wait_for_opponent()

    def handle_start_turn(self, user):
        self.interface.start_turn(user)

    def handle_get_shot_coordinate(self):
        shot = self.interface.get_shot_coordinate()
        if shot == (-1, -1):
            reactor.stop()
        else:
            self.send_query('set_shot_coordinate', shot)

    def handle_incorrect_shot(self, exc):
        self.interface.incorrect_shot(exc)

    def handle_set_miss(self, user, square):
        self.interface.set_miss(user, square)

    def handle_set_shot(self, user, square):
        self.interface.set_shot(user, square)

    def handle_set_sunk_ship(self, user, ship):
        self.interface.set_sunk_ship(user, ship)

    def handle_end_turn(self, user):
        self.interface.end_turn(user)


class CustomClientFactory(ClientFactory):
    def buildProtocol(self, addr):
        return ClientProtocol()


if __name__ == '__main__':
    reactor.connectTCP(ip_address, 8123, CustomClientFactory())
    reactor.run()
