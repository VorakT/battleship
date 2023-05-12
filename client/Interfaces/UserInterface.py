class UserInterface:
    def __init__(self, field_size):
        pass

    def start_session(self):
        pass

    def start_placing_ships(self):
        pass

    def get_ship_place(self, type):
        pass

    def incorrect_ship_placement(self, error, first_square, second_square):
        pass

    def place_ship(self, ship):
        pass

    def start_turn(self, user):
        pass

    def get_shot_coordinate(self):
        pass

    def incorrect_shot(self, error):
        pass

    def set_miss(self, user, square):
        pass

    def set_shot(self, user, square):
        pass

    def set_sunk_ship(self, user, ship):
        pass

    def end_turn(self, user):
        pass

    def end_session(self, won):
        pass

    def wait_for_opponent(self):
        pass
