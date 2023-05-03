class Ship:
    def __init__(self, type, first_square, second_square):
        self.type = type
        self.coordinates = []
        if first_square[0] == second_square[0]:
            for i in range(min(first_square[1], second_square[1]), max(first_square[1], second_square[1]) + 1):
                self.coordinates.append((first_square[0], i))
            self.horizontal = False
        else:
            for i in range(min(first_square[0], second_square[0]), max(first_square[0], second_square[0]) + 1):
                self.coordinates.append((i, first_square[1]))
            self.horizontal = True
        self.shot_squares = 0

    def is_destroyed(self):
        return self.shot_squares == self.type

    def try_shoot(self, square):
        if square not in self.coordinates:
            return False
        self.shot_squares += 1
        return True

    def intersect(self, other_ship):
        coordinates_to_check = set(self.coordinates)
        for x, y in self.coordinates:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    coordinates_to_check.add((x + i, y + j))
        return len(coordinates_to_check & set(other_ship.coordinates)) != 0


class ShotResult:
    def __init__(self, square, has_hit, has_destroyed, ship):
        self.square = square
        self.has_hit = has_hit
        self.has_destroyed = has_destroyed
        self.ship = ship


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