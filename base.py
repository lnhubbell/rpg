# External
import os
import sys
from random import randint
from colorama import init
from threading import Thread
from time import sleep

# Internal
from actors import Player, Rat, SlingShot, Wood, River, Grass, SentientVine


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
        self.time_unit = .05  # in seconds
        self.border_height = 10
        self.get_size()
        self.clear()
        self.border_print()
        self.maps = {}
        self.get_map(0, 0)
        self.player = Player(self)
        self.items = []
        self.items.append(SlingShot(self))
        self.items.append(Wood(self))
        pos_x, pos_y = self.rand_x_y_pos()
        self.vines = []
        self.rat_count = 4
        self.rats = []
        # for rat in range(self.rat_count):
        #     self.rats.append(Rat(self))
        self.time = 0
        self.info_pane = InfoPane(self)
        self.dialogue_history = []
        self.projectiles = []

    def create_map(self, x, y):
        new_map = {}
        self.maps[(x, y)] = new_map
        east_map = self.maps.get((x+1, y))
        west_map = self.maps.get((x-1, y))
        south_map = self.maps.get((x, y+1))
        north_map = self.maps.get((x, y-1))

        rivers = []

        # TODO: get these four chunks into one
        if east_map:
            # there is a map to the east of this new one
            for row in range(2, self.southern_border):
                z_dict = east_map.get((2, row))
                if z_dict:
                    item = self.top_map_value(z_dict)
                    if isinstance(item, River):
                        riv_x = self.eastern_border - 1
                        riv_y = row
                        riv_starting_border = 'e'
                        riv_direction = item.direction
                        rivers.append(
                            River(
                                self, new_map, riv_x, riv_y,
                                riv_starting_border, riv_direction
                            )
                        )
                        break

        if west_map:
            # there is a map to the west of this new one
            for row in range(2, self.southern_border):
                z_dict = west_map.get((self.eastern_border - 1, row))
                if z_dict:
                    item = self.top_map_value(z_dict)
                    if isinstance(item, River):
                        riv_x = 2
                        riv_y = row
                        riv_starting_border = 'w'
                        riv_direction = item.direction
                        rivers.append(
                            River(
                                self, new_map, riv_x, riv_y,
                                riv_starting_border, riv_direction
                            )
                        )
                        break

        if south_map:
            # there is a map to the south of this new one
            for col in range(2, self.eastern_border):
                z_dict = south_map.get((col, 2))
                if z_dict:
                    item = self.top_map_value(z_dict)
                    if isinstance(item, River):
                        riv_x = col
                        riv_y = self.southern_border - 1
                        riv_starting_border = 's'
                        riv_direction = item.direction
                        rivers.append(
                            River(
                                self, new_map, riv_x, riv_y,
                                riv_starting_border, riv_direction
                            )
                        )
                        break

        if north_map:
            # there is a map to the north of this new one
            for col in range(2, self.eastern_border):
                z_dict = north_map.get((col, self.southern_border - 1))
                if z_dict:
                    item = self.top_map_value(z_dict)
                    if isinstance(item, River):
                        riv_x = col
                        riv_y = 2
                        riv_starting_border = 'n'
                        riv_direction = item.direction
                        rivers.append(
                            River(
                                self, new_map, riv_x, riv_y,
                                riv_starting_border, riv_direction
                            )
                        )
                        break

        if not rivers:
            rivers = [River(self, new_map)]

        Grass(self, new_map)
        return new_map

    def get_map(self, x, y):
        self.map_clear()

        if (x, y) in self.maps:
            self.map = self.maps[(x, y)]
        else:
            self.map = self.create_map(x, y)

        self.map_print()
        self.current_map = (x, y)

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

    def print_intersection(self, x, y, target_map=None):
        """prints the topmost object at a given x,y coordinate, if nothing is
        at that coordinate it prints an empty space to ensure the space is
        properly cleared."""

        this_map = target_map or self.map
        z_dict = this_map.get((x, y), {})

        if z_dict:
            map_value = self.top_map_value(z_dict)
            text = map_value.color + map_value.rep
        else:
            text = ' '

        # finally do the actual printing
        self.base_print(x, y, text)
        return True

    def set_map_value(self, x, y, z, map_value, target_map):
        if not isinstance(x, int):
            raise ValueError('x coordinate must be an integer.')
        if not isinstance(y, int):
            raise ValueError('y coordinate must be an integer.')
        if not isinstance(z, int):
            raise ValueError('z coordinate must be an integer.')

        if map_value:
            # If there is already something at this x,y intersection handle it
            if (x, y) in target_map:
                z_dict = target_map[(x, y)]
                if z not in z_dict:
                    z_dict[z] = map_value
                elif z in z_dict:
                    raise EnvironmentError('Uncontrolled spacial collision.')
                # After adding the new z value, grab the top map_value in the
                # pile
                # top_map_value = self.top_map_value(z_dict)

            # otherwise create a new z_dict
            else:
                target_map[(x, y)] = {z: map_value}
                # top_map_value = map_value

            # use the map_value representation to find out what to print
            # text = top_map_value.color + top_map_value.rep

        # If map_value is none, clear this point
        elif map_value is None:
            target_map.get((x, y), {}).pop(z, None)
            # text = ' '

        # finally do the actual printing
        # self.base_print(x, y, text)

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

    def map_clear(self):
        for x in range(2, self.eastern_border):
            for y in range(2, self.southern_border):
                self.base_print(x, y, ' ')

    def map_print(self):
        for x, y in self.map:
            self.print_intersection(x, y)

    def run(self):
        self.base_print_dialogue(story_line_intro)

        def input_thread():
            # first, set player_input to None to indicate that we're waiting
            # for the input. This flag is used to determine if we need to
            # start a new thread or not
            self.player.player_input = None
            # this line will just wait patiently until it gets player_input
            self.player.get_player_input()

        while True:
            # If we're not already waiting for input, start waiting,
            # we will set waiting_for_input to false inside of get_player_input
            # after we get the input
            if not self.player.waiting_for_input:
                self.player.waiting_for_input = True
                thread = Thread(target=input_thread)
                thread.start()

            # Move time foward one unit
            # sleep(self.time_unit)
            self.time += self.time_unit

            # update all the automatic features of the game
            for rat in self.rats:
                rat.be()
            for proj in self.projectiles:
                proj.be()
            for vine in self.vines:
                vine.be()

            self.info_pane.refresh()
            self.player.inventory.show()
            # if there is player input, proccess it here
            if self.player.player_input:
                if self.player.player_input == 'q':
                    os.system("stty echo")
                    self.clear()
                    thread.join()
                    sys.exit()
                self.player.full_move()
                self.player.action()
                # We have processed the input, now dump it
                self.player.player_input = None

    def rand_x_y_pos(self):
        pos_x = randint(2, self.eastern_border - 1)
        pos_y = randint(2, self.southern_border - 1)
        while (pos_x, pos_y) in self.map:
            pos_x = randint(2, self.eastern_border - 1)
            pos_y = randint(2, self.southern_border - 1)

        return pos_x, pos_y

    def base_print_dialogue(self, dialogue):

        time_stamped_dialogue = '%.2f: %s' % (self.time, dialogue)
        if self.dialogue_history:
            previous_dialogue = self.dialogue_history[-1].split(': ')[1]
        else:
            previous_dialogue = ''

        if not dialogue == previous_dialogue:
            for x in range(self.eastern_border):
                for y in range(self.southern_border + 1, self.rows + 1):
                    # self.set_map_value(x, y, 5, None)
                    self.base_print(x, y, ' ')

            self.dialogue_history.append(time_stamped_dialogue)

            for ind, line in enumerate(self.dialogue_history[-5:]):
                # dialogue_line = TextPrint()
                # dialogue_line.rep = line
                # self.set_map_value(
                #     1, self.southern_border + (1 + ind), 5, dialogue_line)
                self.base_print(1, self.southern_border + (1 + ind), line)

    def border_iter(self, rep):
        # South Border
        for num in range(self.eastern_border + 1):
            x, y = num, self.southern_border
            self.base_print(x, y, rep)

        # North Border
        for num in range(self.eastern_border):
            x, y = num, 1
            self.base_print(x, y, rep)

        # East Border
        for num in range(self.southern_border):
            x, y = self.eastern_border, num
            self.base_print(x, y, rep)

        # West Boarder
        for num in range(self.southern_border - 2):
            x, y = 1, num + 2
            self.base_print(x, y, rep)

    def border_print(self):
        self.border_iter('x')

    def border_clear(self):
        self.border_iter(' ')


class InfoPane(object):
    def __init__(self, game):
        self.game = game
        self.western_border = self.game.eastern_border + 2
        self.pos_z = 5
        base = 1
        self.show('Time: %.2f' % self.game.time, base)
        self.show('--- Player ---', base + 1)
        self.show('Name: %s' % self.game.player.name, base + 2)
        self.show('Health: %s' % self.game.player.health, base + 3)
        self.show('Gold: %s' % self.game.player.gold, base + 4)
        self.show('Exp.: %s' % self.game.player.experience, base + 5)
        self.show('Loc.: (%s,%s)' % (self.game.player.pos_x, self.game.player.pos_y), base + 6)
        self.show('Map: %s,%s' % self.game.current_map, base + 7)
        self.show_items(base, 8)
        self.show_chars(base, 18)

    def refresh(self):
        base = 1
        self.show('%.2f' % self.game.time, base, 6)
        self.show('%s' % self.game.player.name, base + 2, 6)
        self.show('%s' % self.game.player.health, base + 3, 8)
        self.show('%s' % self.game.player.gold, base + 4, 6)
        self.show('%s' % self.game.player.experience, base + 5, 6)
        self.show('%s,%s)' % (self.game.player.pos_x, self.game.player.pos_y), base + 6, 7)
        self.show('%s,%s' % self.game.current_map, base + 7, 5)
        self.show_items(base, 8)
        self.show_chars(base, 18)

    def show(self, text, display_height, x_offset=0):
        # clear existing text
        for col in range(self.western_border, self.game.columns - x_offset):
            # self.game.set_map_value(
            #     col + x_offset, display_height, self.pos_z, None)

            self.game.base_print(col + x_offset, display_height, ' ')

        # honestly not positive what's happening here
        # self.game.map.get(
        #     (self.western_border, display_height), {}
        # ).pop(self.pos_z, None)

        # write new text

        self.game.base_print(self.western_border + x_offset, display_height, text)
        # self.game.set_map_value(
        #     self.western_border + x_offset,
        #     display_height, self.pos_z, text_print)

    def show_items(self, base, off_set):
        if self.game.player.items:
            base += off_set
            self.show('Items:', base)
            for ind, item in enumerate(self.game.player.items):
                ind += 1
                self.show("  -%s" % item.name, base + ind)


    def show_spells(self, base, off_set):
        if self.game.player.spells:
            base += off_set
            self.show('Spells:', base)
            for ind, spell in enumerate(self.game.player.spells):
                ind += 1
                self.show("  -%s" % spell.name, base + ind)


    def show_chars(self, base, off_set):
        base += off_set
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
