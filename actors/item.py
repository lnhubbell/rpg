from colorama import Fore


class Item(object):
    def __init__(self, name, game, color='', rep='i', my_map=None):
        self.game = game
        self.my_map = my_map or game.map
        self.pos_x, self.pos_y = self.game.rand_x_y_pos()
        self.pos_z = 10
        self.color = color
        self.rep = rep
        self.print_char()
        self.weight = 1
        self.equip_on = None  # i.e. 'head' or 'feet'
        self.name = name
        self.condition = 100
        self.actions = {
            'n': self.drop
        }

    def drop(self):
        pass

    def print_char(self):
        self.game.set_map_value(self.pos_x, self.pos_y, self.pos_z, self, self.my_map)


class Wood(Item):
    def __init__(self, game):
        Item.__init__(self, 'Wood', game)


class FlintandSteel(Item):
    def __init__(self, game):
        Item.__init__(self, 'Flint and Steel', game)
        self.actions = {
            'f': self.fire
        }

    def fire(self):
        self.game.base_print_dialogue('Sparks fly from your fingers...')


class SlingShot(Item):
    def __init__(self, game):
        Item.__init__(self, 'SlingShot', game, color=Fore.BLUE, rep='s')
        self.player = None
        self.actions = {
            'p': self.load_sling_shot,
            'i': self.sling,
            'j': self.sling,
            'k': self.sling,
            'l': self.sling,
        }

    def load_sling_shot(self):
        self.player.long_range_prepared = True
        self.game.base_print_dialogue('SlingShot loaded!')

    def sling(self):
        self.player.long_range_attack(8, 3, .75, 'SlingShot')
