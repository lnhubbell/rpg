# External
import os
from random import randint
from colorama import init


# Internal
from actors import Player, Rat, SlingShot, Wood, River, Grass


init(autoreset=True)

# prevent anything the user types in from being echo'd by the terminal
os.system("stty -echo")


story_line_intro = "You're on a cold plain, there are rocks scattered about. You can hear the sounds of rats..."  # NOQA


class TextPrint:
    rep = ''
    color = ''

class Game(object):
    ENCOUNTERS = []

    def __init__(self):
        self.border_height = 10
        self.get_size()
        self.clear()
        self.map = {}
        self.biomes = (Grass(self), River(self))
        self.player = Player(self)
        self.items = []
        self.items.append(SlingShot(self))
        self.items.append(Wood(self))
        self.rat_count = 3
        self.rats = []
        for rat in range(self.rat_count):
            self.rats.append(Rat(self))
        self.time = 0
        self.print_map_border()
        self.info_pane = InfoPane(self)
        self.dialogue_history = []
        self.projectiles = []

    def temp_print(self, x, y, text, map_value=None):
        print("\033[%s;%sH%s" % (y, x, text))

    def get_map_text(self, x, y):
        text = None
        if self.map.get((x, y)):
            z_dict = self.map[(x, y)]
            if len(z_dict) == 1:
                text = list(z_dict.values())[0]
            elif len(z_dict) > 1:
                try:
                    text = sorted(z_dict.items(), key=lambda x: -x[0])[0][1]
                except TypeError:
                    print(z_dict)
                    raise
            else:
                raise EnvironmentError('x,y exist but there is no z_dict')
            if not isinstance(text, str):
                if hasattr(text, 'rep'):
                    text = text.rep
                else:
                    print(type(text))
                    raise ValueError('%s is not a string!' % text)
        if text is None:
            text = ' '

        return text

    def top_map_value(self, z_dict):
        return sorted(z_dict.items(), key=lambda x: -x[0])[0][1]

    def print_intersection(self, x, y):
        try:
            z_dict = self.map[(x, y)]
        except KeyError:
            return False
        if not z_dict:
            return False

        map_value = self.top_map_value(z_dict)
        text = map_value.color + map_value.rep
        # finally do the actual printing
        self.base_print(x, y, text)
        return True

    def set_map_value(self, x, y, z, map_value):
        if not isinstance(x, int):
            raise ValueError('x coordinate must be an integer.')
        if not isinstance(y, int):
            raise ValueError('y coordinate must be an integer.')
        if not isinstance(z, int):
            raise ValueError('z coordinate must be an integer.')

        if map_value:
            # If there is already something at this x,y intersection handle it
            if (x, y) in self.map:
                z_dict = self.map[(x, y)]
                if z not in z_dict:
                    z_dict[z] = map_value
                elif z in z_dict:
                    raise EnvironmentError('Uncontrolled spacial collision.')
                # After adding the new z value, grab the top map_value in the
                # pile
                top_map_value = self.top_map_value(z_dict)

            # otherwise create a new z_dict
            else:
                self.map[(x, y)] = {z: map_value}
                top_map_value = map_value

            # use the map_value representation to find out what to print
            text = top_map_value.color + top_map_value.rep

        # If map_value is none, clear this point
        elif map_value is None:
            self.map.get((x, y), {}).pop(z, None)
            text = ' '

        # finally do the actual printing
        self.base_print(x, y, text)

    def base_print(self, x, y, text):
        print("\033[%s;%sH%s" % (y, x, text))

    def get_size(self):
        rows, columns = os.popen('stty size', 'r').read().split()
        self.rows = int(rows) - 1
        self.columns = int(columns)
        self.southern_border = self.rows - 8
        self.eastern_border = self.columns - 25

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_map_border(self):
        class Border:
            rep = 'x'
            color = ''
        # South Border
        for num in range(self.eastern_border + 1):
            self.set_map_value(num, self.southern_border, self.border_height, Border)
        # North Border
        for num in range(self.eastern_border):
            self.set_map_value(num, 1, self.border_height, Border)
        # East Border
        for num in range(self.southern_border):
            self.set_map_value(self.eastern_border, num, self.border_height, Border)
        # West Boarder
        for num in range(self.southern_border - 2):
            self.set_map_value(1, num + 2, self.border_height, Border)


        # self.print_gateway()

    def print_gateway(self):
        gateway_length = 5
        gateway_edge = randint(0, 3)
        if gateway_edge in (0, 1):
            gateway_pos = randint(2, self.southern_border - 8)
            if gateway_edge == 1:
                for num in range(gateway_length):
                    self.set_map_value(1, gateway_pos + num, self.border_height, None)
            else:
                for num in range(gateway_length):
                    self.set_map_value(self.eastern_border, gateway_pos + num, self.border_height, None)
        else:
            gateway_pos = randint(2, self.eastern_border - 8)
            if gateway_edge == 2:
                for num in range(gateway_length):
                    self.set_map_value(gateway_pos + num, 1, self.border_height, None)
            else:
                for num in range(gateway_length):
                    self.set_map_value(gateway_pos + num, self.southern_border, self.border_height, None)

    def run(self):
        self.base_print_dialogue(story_line_intro)
        while True:
            self.time += 1
            self.info_pane.refresh()
            self.player.get_player_input()
            self.player.inventory.show()
            self.player.full_move()
            self.player.action()
            for rat in self.rats:
                rat.be()
            for proj in self.projectiles:
                proj.be()

    def rand_x_y_pos(self):
        pos_x = randint(2, self.eastern_border - 1)
        pos_y = randint(2, self.southern_border - 1)
        while (pos_x, pos_y) in self.map:
            pos_x = randint(2, self.eastern_border - 1)
            pos_y = randint(2, self.southern_border - 1)

        return pos_x, pos_y

    def base_print_dialogue(self, dialogue):
        time_stamped_dialogue = '%s: %s' % (self.time, dialogue)
        for x in range(self.eastern_border):
            for y in range(self.southern_border + 1, self.rows + 1):
                self.set_map_value(x, y, 5, None)

        self.dialogue_history.append(time_stamped_dialogue)

        for ind, line in enumerate(self.dialogue_history[-5:]):
            dialogue_line = TextPrint()
            dialogue_line.rep = line
            self.set_map_value(
                1, self.southern_border + (1 + ind), 5, dialogue_line)


class InfoPane(object):
    def __init__(self, game):
        self.game = game
        self.western_border = self.game.eastern_border + 2
        self.pos_z = 5

    def refresh(self):
        base = 1
        self.show('Time: %s' % self.game.time, base)
        self.show('--- Player ---', base + 1)
        self.show('Name: %s' % self.game.player.name, base + 2)
        self.show('Health: %s' % self.game.player.health, base + 3)
        self.show('Gold: %s' % self.game.player.gold, base + 4)
        self.show('Exp.: %s' % self.game.player.experience, base + 5)
        self.show_items(base)

        self.show_chars(base)

    def show(self, text, display_height):
        text_print = TextPrint()
        text_print.rep = text

        for col in range(self.western_border, self.game.columns):
            self.game.set_map_value(col, display_height, self.pos_z, None)
        self.game.map.get(
            (self.western_border, display_height), {}).pop(self.pos_z, None)
        self.game.set_map_value(
            self.western_border, display_height, self.pos_z, text_print)

    def show_items(self, base):
        if self.game.player.items:
            base += 6
            self.show('Items:', base)
            for ind, item in enumerate(self.game.player.items):
                ind += 1
                self.show("  -%s" % item.name, base + ind)

    def show_chars(self, base):
        base += 15
        self.show('--- OTHER CHARS ---', base)
        for ind, rat in enumerate(self.game.rats):
            ind += 1
            ind *= 3
            self.show(
                '%s named: %s.' % (rat.species, rat.name), base + (ind - 1))
            self.show('Health: %s' % rat.health, base + ind)

if __name__ == '__main__':
    game = Game()
    game.run()
