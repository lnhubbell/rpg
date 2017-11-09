from colorama import Fore
from random import randint, sample, choice

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
    def __init__(self, game, x=None, y=None, starting_border=None, direction=None):
        Biome.__init__(self, 'River', game)
        self.color = Fore.CYAN
        self.rep = '0'
        self.pos_z = 1
        self.pos_x = x
        self.pos_y = y

        if x is None and y is None and starting_border is None and direction is None:
            # Starting a new river, choose which side it starts on
            starting_border = choice(['n', 'e', 's', 'w'])

            rep_map = {
                'n': 'v',
                'e': '<',
                's': '^',
                'w': '>',
            }

            direction = rep_map[starting_border]

            # starts on the east
            if starting_border == 'e':
                self.pos_x = game.eastern_border - 1
                self.pos_y = randint(2, game.southern_border - 1)

            # starts on the south
            elif starting_border == 's':
                self.pos_x = randint(2, game.eastern_border - 1)
                self.pos_y = game.southern_border - 1

            # starts on the west
            elif starting_border == 'w':
                self.pos_x = 2
                self.pos_y = randint(2, game.southern_border - 1)

            # starts on the north
            elif starting_border == 'n':
                self.pos_x = randint(2, game.eastern_border - 1)
                self.pos_y = 2
        elif x is None:
            raise(ValueError('If <x> is None all values must be None.'))
        elif y is None:
            raise(ValueError('If <y> is None all values must be None.'))
        elif starting_border is None:
            raise(ValueError(
                'If <starting_border> is None all values must be None.'))
        elif direction is None:
            raise(ValueError(
                'If <direction> is None all values must be None.'))

        self.direction = direction
        self.rep = direction

        while (
            self.pos_x < game.eastern_border and
            self.pos_y < game.southern_border and
            self.pos_x > 1 and
            self.pos_y > 1
        ):

            if starting_border not in ['n', 'e', 's', 'w']:
                raise ValueError('starting_border is not of correct type')
            self.print_char()

            # traveling due West
            if starting_border == 'e':
                self.pos_x -= 1
                self.pos_y += randint(-1, 1)

            # traveling due north
            elif starting_border == 's':
                self.pos_y -= 1
                self.pos_x += randint(-1, 1)

            # traveling due south
            elif starting_border == 'n':
                self.pos_y += 1
                self.pos_x += randint(-1, 1)

            # traveling due east
            elif starting_border == 'w':
                self.pos_x += 1
                self.pos_y += randint(-1, 1)


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
            if rand < 2 or len(self.all_grass_locs()) == 0:
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
                self.pos_x, self.pos_y = sample(self.all_grass_locs(), 1)[0]
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

    def all_grass_locs(self):
        locs = []
        for loc, z_dict in self.game.map.items():
            for item in z_dict.values():
                if isinstance(item, Grass):
                    locs.append(loc)
                    break

        return locs

