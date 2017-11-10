from colorama import Fore


class Spell(object):
    def __init__(self, name, game, color='', rep='5', my_map=None):
        self.game = game
        self.my_map = my_map or game.map
        self.pos_x, self.pos_y = self.game.rand_x_y_pos()
        self.pos_z = 10
        self.color = color
        self.rep = rep
        self.print_char()

        self.name = name

        self.actions = {
            'o': self.fire,
        }

    def prepare_spell(self):
        self.game.player.spell_prepared = True
        self.game.base_print_dialogue('Magic harnessed!')

    def fire(self):
        self.game.player.spell_prepared = False

    def print_char(self):
        self.game.set_map_value(self.pos_x, self.pos_y, self.pos_z, self, self.my_map)


class RingOfFire(Spell):
    def __init__(self, game):
        Spell.__init__(self, 'Ring of Fire', game)
