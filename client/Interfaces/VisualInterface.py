from os import environ

environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from Interfaces.UserInterface import UserInterface
from Interfaces.visual_config import WIDTH, HEIGHT, FPS
from pygame.color import THECOLORS
from Interfaces.console_interface_config import session_messages as messages
from twisted.internet.task import LoopingCall
from twisted.internet import reactor


class VisualInterface(UserInterface):
    def __init__(self, field_size):
        self.field_size = field_size
        self.placed_ships = []
        self.misses = [[], []]
        self.shots = [[], []]
        self.sunk_ships = [[], []]
        self.load_sprites()
        self.loop = None
        self.wrong_squares = []

    def load_sprites(self):
        tile_width = WIDTH / self.field_size
        tile_height = HEIGHT / self.field_size
        self.water_tile = pygame.transform.scale(pygame.image.load("sprites/water_tile.png"),
                                                 (tile_width - 2, tile_height - 2))
        self.fire_tile = pygame.transform.scale(pygame.image.load("sprites/fire_tile.png"),
                                                (tile_width - 2, tile_height - 2))
        two_tile_ship = pygame.transform.scale(pygame.image.load("sprites/2_tile_ship.png"),
                                               (tile_width * 2, tile_height))
        three_tile_ship = pygame.transform.scale(pygame.image.load("sprites/3_tile_ship.png"),
                                                 (tile_width * 3, tile_height))
        four_tile_ship = pygame.transform.scale(pygame.image.load("sprites/4_tile_ship.png"),
                                                (tile_width * 4 - 2, tile_height - 2))
        two_tile_ship.set_colorkey((188, 188, 188))
        three_tile_ship.set_colorkey((188, 188, 188))
        four_tile_ship.set_colorkey((188, 188, 188))
        self.ship_surf = {2: two_tile_ship, 3: three_tile_ship, 4: four_tile_ship}
        rotated_two_tile_ship = pygame.transform.scale(pygame.image.load("sprites/2_tile_ship.png"),
                                                       (tile_height * 2, tile_width))
        rotated_two_tile_ship = pygame.transform.rotate(rotated_two_tile_ship, 270)
        rotated_three_tile_ship = pygame.transform.scale(pygame.image.load("sprites/3_tile_ship.png"),
                                                         (tile_height * 3, tile_width))
        rotated_three_tile_ship = pygame.transform.rotate(rotated_three_tile_ship, 270)
        rotated_four_tile_ship = pygame.transform.scale(pygame.image.load("sprites/4_tile_ship.png"),
                                                        (tile_height * 4 - 2, tile_width - 2))
        rotated_four_tile_ship = pygame.transform.rotate(rotated_four_tile_ship, 270)
        rotated_two_tile_ship.set_colorkey((188, 188, 188))
        rotated_three_tile_ship.set_colorkey((188, 188, 188))
        rotated_four_tile_ship.set_colorkey((188, 188, 188))
        self.rotated_ship_surf = {2: rotated_two_tile_ship, 3: rotated_three_tile_ship, 4: rotated_four_tile_ship}

    def message(self, text, seconds):
        frames = 0
        font = pygame.font.SysFont('arial', 20)
        while frames < seconds * FPS:
            self.clock.tick(FPS)
            self.screen.fill(THECOLORS['blue'])
            surf = font.render(text, True, THECOLORS['black'])
            self.screen.blit(surf, (self.screen.get_width() / 2 - surf.get_width() / 2,
                                    self.screen.get_height() / 2 - surf.get_height() / 2))
            pygame.event.pump()
            frames += 1
            pygame.display.flip()

    def start_session(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

    def start_placing_ships(self):
        self.message(messages['set_message'], 1.5)

    def draw_board_while_placing_ships(self):
        tile_width = WIDTH / self.field_size
        tile_height = HEIGHT / self.field_size
        self.screen.fill((188, 188, 188))
        for x, y in self.misses[1]:
            self.screen.blit(self.water_tile, (x * tile_width, y * tile_height))
        for x, y in self.shots[1]:
            self.screen.blit(self.fire_tile, (x * tile_width, y * tile_height))
        for ship in self.placed_ships:
            if ship.horizontal:
                ship_surf = self.ship_surf[len(ship.coordinates)]
            else:
                ship_surf = self.rotated_ship_surf[len(ship.coordinates)]
            self.screen.blit(ship_surf, (tile_width * ship.coordinates[0][0], tile_height * ship.coordinates[0][1]))
        for i in range(len(self.wrong_squares)):
            (x, y), frames = self.wrong_squares[i]
            pygame.draw.rect(self.screen, THECOLORS['red'], (tile_width * x, tile_height * y, tile_width, tile_height))
            self.wrong_squares[i][1] -= 1
        for i in range(len(self.wrong_squares) - 1, -1, -1):
            if self.wrong_squares[i][1] == 0:
                self.wrong_squares.pop(i)
                i += 1
        for x in range(1, self.field_size):
            pygame.draw.line(self.screen, THECOLORS['black'], (x * tile_width - 1, 0), (x * tile_width - 1, HEIGHT), 2)
        for y in range(1, self.field_size):
            pygame.draw.line(self.screen, THECOLORS['black'], (0, y * tile_height - 1), (WIDTH, y * tile_height - 1), 2)

    def get_ship_surf(self, type, horizontal):
        if horizontal:
            surf = self.ship_surf[type]
        else:
            surf = self.rotated_ship_surf[type]
        return surf

    def get_pressed_square(self):
        tile_width = WIDTH / self.field_size
        tile_height = HEIGHT / self.field_size
        pos = pygame.mouse.get_pos()
        return int(pos[0] // tile_width), int(pos[1] // tile_height)

    def get_ship_place(self, type):
        tile_width = WIDTH / self.field_size
        tile_height = HEIGHT / self.field_size
        hor_ship = self.get_ship_surf(type, True)
        ver_ship = self.get_ship_surf(type, False)
        mode = 0
        ship = hor_ship
        while True:
            self.clock.tick(FPS)
            self.draw_board_while_placing_ships()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (-1, -1), (-1, -1)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if mode == 0:
                        ship = ver_ship
                    else:
                        ship = hor_ship
                    mode ^= 1
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    square = self.get_pressed_square()
                    second_square = square
                    if mode == 0:
                        second_square = (second_square[0] + type - 1, second_square[1])
                    else:
                        second_square = (second_square[0], second_square[1] + type - 1)
                    return square, second_square
            pos = pygame.mouse.get_pos()
            self.screen.blit(ship, (pos[0] - tile_width / 2, pos[1] - tile_height / 2))
            pygame.display.flip()

    def incorrect_ship_placement(self, error, first_square, second_square):
        print(error)
        self.wrong_squares.clear()
        for i in range(min(first_square[0], second_square[0]), max(first_square[0], second_square[0]) + 1):
            for j in range(min(first_square[1], second_square[1]), max(first_square[1], second_square[1]) + 1):
                if 0 <= i < self.field_size and 0 <= j < self.field_size:
                    self.wrong_squares.append([(i, j), FPS * 2])

    def place_ship(self, ship):
        self.placed_ships.append(ship)

    def start_turn(self, user):
        if user == 0:
            self.message(messages['turn_message_0'], 1.5)
            if self.loop is not None:
                self.loop.stop()
                self.loop = None
        else:
            self.message(messages['turn_message_1'], 1.5)
            if self.loop is None:
                self.loop = LoopingCall(self.draw_board_while_opponent_turn)
                self.loop.start(1.0 / FPS)

    def draw_board_while_shooting(self):
        tile_width = WIDTH / self.field_size
        tile_height = HEIGHT / self.field_size
        self.screen.fill((188, 188, 188))
        for x, y in self.misses[0]:
            self.screen.blit(self.water_tile, (x * tile_width, y * tile_height))
        for x, y in self.shots[0]:
            self.screen.blit(self.fire_tile, (x * tile_width, y * tile_height))
        for ship in self.sunk_ships[0]:
            if ship.horizontal:
                ship_surf = self.ship_surf[len(ship.coordinates)]
            else:
                ship_surf = self.rotated_ship_surf[len(ship.coordinates)]
            self.screen.blit(ship_surf, (tile_width * ship.coordinates[0][0], tile_height * ship.coordinates[0][1]))
        for x in range(1, self.field_size):
            pygame.draw.line(self.screen, THECOLORS['black'], (x * tile_width - 1, 0), (x * tile_width - 1, HEIGHT), 2)
        for y in range(1, self.field_size):
            pygame.draw.line(self.screen, THECOLORS['black'], (0, y * tile_height - 1), (WIDTH, y * tile_height - 1), 2)
        pygame.display.flip()

    def get_shot_coordinate(self):
        while True:
            self.clock.tick(FPS)
            self.draw_board_while_shooting()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1, -1
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    square = self.get_pressed_square()
                    return square

    def incorrect_shot(self, error):
        print(error)

    def show_board(self, seconds, show_function):
        frames = 0
        while frames < seconds * FPS:
            self.clock.tick(FPS)
            show_function()
            pygame.event.pump()
            frames += 1

    def set_miss(self, user, square):
        self.misses[user].append(square)
        if user == 0:
            self.show_board(1.5, self.draw_board_while_shooting)
        else:
            self.show_board(1.5, self.draw_board_while_opponent_turn)

    def set_shot(self, user, square):
        self.shots[user].append(square)

    def set_sunk_ship(self, user, ship):
        self.sunk_ships[user].append(ship)

    def end_turn(self, user):
        pass

    def end_session(self, won):
        if won == 0:
            self.show_board(1.5, self.draw_board_while_shooting)
            self.message(messages['end_message_0'], 2)
        else:
            self.message(messages['end_message_1'], 2)
            if self.loop is not None:
                self.loop.stop()
                self.loop = None

    def wait_for_opponent(self):
        self.message(messages['wait_message'], 1)
        self.loop = LoopingCall(self.draw_board_while_opponent_turn)
        self.loop.start(1.0 / FPS)

    def draw_board_while_opponent_turn(self):
        self.draw_board_while_placing_ships()
        pygame.display.flip()
        pygame.event.pump()
