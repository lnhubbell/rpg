from colorama import Fore
from random import randint, sample

class Biome(object):
    def __init__(self, name, game):
        self.game = game
        self.color = ''
        self.rep = 'i'
        self.name = name
        self.pos_x, self.pos_y = self.game.rand_x_y_pos()
        self.pos_z = 0

    def print_char(self):
        self.game.set_map_value(self.pos_x, self.pos_y, self.pos_z, self)


class River(Biome):
    def __init__(self, game):
        Biome.__init__(self, 'River', game)
        self.color = Fore.CYAN
        self.rep = '.'
        self.pos_z = 1

        rand = randint(0, 1)
        # self starts on the east
        if rand:
            self.pos_x = game.eastern_border - 1
            self.pos_y = randint(2, game.southern_border - 1)
        # self starts on the north
        else:
            self.pos_x = randint(2, game.eastern_border - 1)
            self.pos_y = game.southern_border - 1

        while self.pos_x > 1 and self.pos_y > 1:
            self.print_char()
            if rand:
                self.pos_x -= 1
                self.pos_y += randint(-1, 1)
            else:
                self.pos_y -= 1
                self.pos_x += randint(-1, 1)


class Grass(Biome):
    def __init__(self, game):
        Biome.__init__(self, 'Grass', game)
        self.color = Fore.GREEN
        self.rep = '#'
        self.pos_z = 1

        total_area = game.southern_border * game.eastern_border
        grass_count = randint(int(total_area*.02), int(total_area*.1))
        for blade in range(grass_count):
            rand = randint(0, 15)
            self.pos_z = 0
            if rand < 2 or len(game.map) == 0:
                self.pos_x = None
                self.pos_y = None
                # we want to generate this once, then keep trying until we get
                # fresh values
                while (self.pos_x, self.pos_y) in game.map or self.pos_x is None:
                    self.pos_x = randint(2, game.eastern_border - 1)
                    self.pos_y = randint(2, game.southern_border - 1)
            else:
                # print(game.map)
                # self.pos_x, self.pos_y = sample(game.map, 1)[0]
                self.pos_x, self.pos_y = sample(game.map.keys(), 1)[0]
                while (self.pos_x, self.pos_y) in game.map:
                    nudge = randint(1, 4)
                    if nudge == 1 and self.pos_x < (game.eastern_border - 1):
                        self.pos_x += 1
                    elif nudge == 2 and self.pos_x > (2):
                        self.pos_x -= 1
                    elif nudge == 3 and self.pos_y < (game.southern_border - 1):
                        self.pos_y += 1
                    elif nudge == 4 and self.pos_y > (2):
                        self.pos_y -= 1

            # import time; time.sleep(.003)
            self.print_char()

            self.pos_x = self.pos_y = self.pos_z = None


# class Border(Biome):
#     def __init__(self, game):
#         Biome.__init__(self, 'Border', game)
#         self.color = ''
#         self.rep = 'x'
#         self.pos_z = 10
#         # South Border
#         for num in range(game.eastern_border + 1):
#             self.pos_x, self.pos_y = num, game.southern_border
#             self.print_char()

#         # North Border
#         for num in range(game.eastern_border):
#             self.pos_x, self.pos_y = num, 1
#             self.print_char()

#         # East Border
#         for num in range(game.southern_border):
#             self.pos_x, self.pos_y = game.eastern_border, num
#             self.print_char()

#         # West Boarder
#         for num in range(game.southern_border - 2):
#             self.pos_x, self.pos_y = 1, num + 2
#             self.print_char()
