from GameLogic import *
from config import structure


class Session:
    def __init__(self, field_size, protocol1, protocol2):
        self.game_data = GameData(field_size)
        self.protocols = (protocol1, protocol2)
        self.ships_placed = [0, 0]

    def sent_identical_information(self, type, data=None):
        try:
            for protocol in self.protocols:
                protocol.send_query(type, data)
        except Exception as exc:
            print(exc)
            return False
        return True

    def sent_personalized_information(self, type, user, data=None):
        try:
            if data is not None:
                self.protocols[0].send_query(type, (user, data))
                self.protocols[1].send_query(type, (user ^ 1, data))
            else:
                self.protocols[0].send_query(type, user)
                self.protocols[1].send_query(type, user ^ 1)
        except Exception as exc:
            print(exc)
            return False
        return True

    def sent_one_information(self, protocol, type, data=None):
        try:
            protocol.send_query(type, data)
        except Exception as exc:
            print(exc)
            return False
        return True

    def set_shot_coordinate(self, shot, user):
        try:
            shot_result = self.game_data.make_shot(user ^ 1, shot)
        except Exception as exc:
            if not self.sent_one_information(self.protocols[user], 'incorrect_shot', exc):
                return False
            if not self.get_shot_coordinate(user):
                return False
            return True
        if not shot_result.has_hit:
            if not self.sent_personalized_information('set_miss', user, shot_result.square):
                return False
            if not self.end_turn(user):
                return False
            return True
        if not self.sent_personalized_information('set_shot', user, shot_result.square):
            return False
        if shot_result.has_destroyed:
            if not self.sent_personalized_information('set_sunk_ship', user, shot_result.ship):
                return False
            if self.game_data.check_end(user ^ 1):
                if not self.game_end(user):
                    return False
                return True
        self.get_shot_coordinate(user)
        return True

    def end_turn(self, user):
        if self.game_data.check_end(user ^ 1):
            if not self.game_end(user):
                return False
            return True
        if not self.sent_personalized_information('end_turn', user):
            return False
        if not self.make_turn(user ^ 1):
            return False
        return True

    def get_shot_coordinate(self, user):
        if not self.sent_one_information(self.protocols[user], 'get_shot_coordinate'):
            return False
        return True

    def make_turn(self, user):
        if not self.sent_personalized_information('start_turn', user):
            return False
        if not self.get_shot_coordinate(user):
            return False
        return True

    def place_one_ship(self, user, place):
        try:
            ship = self.game_data.place_ship(user, structure[self.ships_placed[user]], place[0], place[1])
        except Exception as exc:
            if not self.sent_one_information(self.protocols[user], 'incorrect_ship_placement', exc):
                return False
            self.get_ship_place(user)
            return True
        if not self.sent_one_information(self.protocols[user], 'place_ship', ship):
            return False
        self.ships_placed[user] += 1
        if self.ships_placed[user] < len(structure):
            if not self.get_ship_place(user):
                return False
        elif self.ships_placed[user ^ 1] < len(structure):
            if not self.sent_one_information(self.protocols[user], 'wait_for_opponent'):
                return False
        else:
            if not self.make_turn(0):
                return False
        return True

    def get_ship_place(self, user):
        if not self.sent_one_information(self.protocols[user], 'get_ship_place', structure[self.ships_placed[user]]):
            return False
        return True

    def place_ships(self, user):
        if not self.sent_one_information(self.protocols[user], 'start_placing_ships'):
            return False
        if not self.get_ship_place(user):
            return False
        return True

    def start(self):
        if not self.sent_identical_information('start_session'):
            return False
        if not self.place_ships(0):
            return False
        if not self.place_ships(1):
            return False
        return True
        user = 0
        other_user = 1
        game_going = True
        while game_going:
            self.make_turn(user)
            if self.game_data.check_end(other_user):
                game_going = False
                won = user
            user, other_user = other_user, user
        if not self.check_protocols():
            return
        for protocol in self.protocols:
            protocol.send_query('end_session', won)
            protocol.transport.loseConnection()

    def game_end(self, won):
        self.sent_personalized_information('end_session', won)
        try:
            self.protocols[0].transport.loseConnection()
        except:
            pass
        try:
            self.protocols[1].transport.loseConnection()
        except:
            pass
