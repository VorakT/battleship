from Query import Ship, ShotResult


class UserData:
    def __init__(self, field_size):
        self.ships = []
        self.shots = []
        self.field_size = field_size
        self.ships_alive = 0

    def place_ship(self, type, first_square, second_square):
        for i in first_square:
            if i < 0 or i >= self.field_size:
                raise Exception('Out of bounds')
        for i in second_square:
            if i < 0 or i >= self.field_size:
                raise Exception('Out of bounds')
        if first_square[0] != second_square[0] and first_square[1] != second_square[1]:
            raise Exception('Squares not in one line')
        if abs(first_square[0] - second_square[0]) + abs(first_square[1] - second_square[1]) + 1 != type:
            raise Exception('Not the right length')
        ship = Ship(type, first_square, second_square)
        for i in self.ships:
            if ship.intersect(i):
                raise Exception('Intersects with your other ship')
        self.ships.append(ship)
        self.ships_alive += 1
        return ship

    def make_shot(self, square):
        for i in square:
            if i < 0 or i >= self.field_size:
                raise Exception('Out of bounds')
        if square in self.shots:
            raise Exception('You have already shot there')
        self.shots.append(square)
        for ship in self.ships:
            if ship.try_shoot(square):
                if ship.is_destroyed():
                    self.ships_alive -= 1
                return ShotResult(square, True, ship.is_destroyed(), ship)
        return ShotResult(square, False, False, None)

    def has_lost(self):
        return self.ships_alive == 0


class GameData:
    def __init__(self, field_size):
        self.user_data = [UserData(field_size), UserData(field_size)]

    def place_ship(self, user_ind, type, first_square, second_square):
        return self.user_data[user_ind].place_ship(type, first_square, second_square)

    def make_shot(self, user_ind, square):
        return self.user_data[user_ind].make_shot(square)

    def check_end(self, user_ind):
        return self.user_data[user_ind].has_lost()