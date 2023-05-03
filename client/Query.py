class Query:
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


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
