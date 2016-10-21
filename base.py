import os
import sys
import time
from random import randint, sample, random
from math import sqrt
from colorama import Fore, Back, Style, init

init(autoreset=True)

# prevent anything the user types in from being echo'd by the terminal
os.system("stty -echo")

male_names = {
    'Kendall', 'Antonio', 'Garry', 'Dewitt', 'Douglas', 'Wilford', 'Wiley',
    'Casey', 'Brian', 'Rocco', 'Michael', 'Gregg', 'Jesse', 'Darrick',
    'Derrick', 'Dong', 'Tim', 'Donovan', 'Man', 'Oswaldo', 'Steve', 'Kareem',
    'Abel', 'Stanley', 'Gustavo', 'Heriberto', 'Marcus', 'Darryl', 'Kerry',
    'Monty', 'Elliot', 'Brant', 'Perry', 'Leonardo', 'Lonny', 'Santos',
    'Delbert', 'Ahmed', 'Darron', 'Kendrick', 'Danial', 'Sam', 'Otto',
    'Lawrence', 'Gerard', 'Victor', 'Jimmie', 'Dorian', 'Alberto', 'Craig'
}
female_names = {
    'Tobi', 'Addie', 'Myriam', 'Danette', 'Jacquelin', 'Shawana', 'Erica',
    'Eleanore', 'Maire', 'Gabriella', 'Reva', 'Elaina', 'Margene', 'Kisha',
    'Leonor', 'Jada', 'Marsha', 'Chau', 'Krystle', 'Dorcas', 'Sofia', 'Kandis',
    'Lois', 'Rochel', 'Lavina', 'Esta', 'Slyvia', 'Nicola', 'Yoko', 'Kathrine',
    'Keira', 'Luisa', 'Gracie', 'Karlene', 'Heather', 'Katlyn', 'Piper',
    'Carita', 'Elenor', 'Izola', 'Myra', 'Jacquline', 'Shaunta', 'Florida',
    'Brandy', 'Nada', 'Jenell', 'Shawna', 'Becki', 'Marcelle'
}
all_names = male_names | female_names

story_line_intro = "You're on a cold plain, there are rocks scattered about. You can hear the sounds of rats..."  # NOQA


def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys
    import tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()


class Biome(object):
    def __init__(self, name, game):
        self.game = game
        self.color = ''
        self.rep = 'i'
        self.name = name
        self.pos_x, self.pos_y = self.game.rand_x_y_pos()
        self.pos_z = 0

    def print_char(self):
        self.game.base_print(
            self.pos_x, self.pos_y, self.pos_z, self.color + self.rep, self)


class River(Biome):
    def __init__(self, game):
        Biome.__init__(self, 'River', game)
        self.color = Fore.CYAN
        self.rep = '.'
        self.pos_z = 1


class Item(object):
    def __init__(self, name, game, color='', rep='i'):
        self.game = game
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
        self.game.base_print(
            self.pos_x, self.pos_y, self.pos_z, self.color + self.rep, self)


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


class Creature(object):
    VALID_MOVES = {'a', 'w', 's', 'd'}

    def __init__(self, game):
        self.obstacle = {
            'd': False,
            's': False,
            'w': False,
            'a': False,
        }
        self.color = ''
        self.rep = 'w'
        self.game = game
        self.pos_x, self.pos_y = self.game.rand_x_y_pos()
        self.pos_z = 10
        # keep track of one previous move for the character
        self.prev_pos_x = None
        self.prev_pos_y = None
        self.prev_pos_z = None
        self.health = 10
        self.name = sample(all_names, 1)[0]
        self.under_attack = False
        self.dead = False

    def print_char(self):
        self.game.base_print(
            self.pos_x, self.pos_y, self.pos_z, self.color + self.rep, self)

    def show_hit(self):
        main_color = self.color
        self.color = Fore.RED
        self.print_char()
        time.sleep(.15)
        self.color = main_color
        self.print_char()

    def clear_prev(self):
        # if the thing in your previous space is you

        if self.game.map.get(
                (self.prev_pos_x, self.prev_pos_y), {}).get(
                self.prev_pos_z, None) in {self, self.rep}:
            # then delete your old self
            self.game.base_print(
                self.prev_pos_x, self.prev_pos_y, self.prev_pos_z, ' ')
        # otherwise, something else has already overwritten your old self, and
        # we don't want to delete that!

    def set_prev(self):
        self.prev_pos_x = self.pos_x
        self.prev_pos_y = self.pos_y
        self.prev_pos_z = self.pos_z

    def choose_move(self):
        # random
        if not self.under_attack:
            move = sample(self.VALID_MOVES, 1)[0]
        else:
            # agro
            target_x = self.game.player.pos_x
            target_y = self.game.player.pos_y

            possible_moves = []
            if self.pos_x > target_x:
                possible_moves.append('a')
            else:
                possible_moves.append('d')

            if self.pos_y > target_y:
                possible_moves.append('w')
            else:
                possible_moves.append('s')

            move = sample(possible_moves, 1)[0]

        return move

    def choose_and_move(self):
        move = self.choose_move()
        return self.move_char(move)

    def check_obstacle(self, x, y, z):
        # check to see if there is an obstacle at a give x,y coordinate
        # If its in the map
        if (x, y, z) in self.game.map:
            # and its a biome
            if isinstance(self.game.map[(x, y, z)], Biome):
                # then its not an obstacle
                return False
            # otherwise it is
            return True
        # if it's not in the map, its not an obstacle
        return False

    def move_char(self, direction):
        self.obstacle['d'] = (
            (self.pos_x == (self.game.columns - 1)) or
            (self.check_obstacle((self.pos_x + 1), self.pos_y, self.pos_z))
        )
        self.obstacle['a'] = (
            (self.pos_x == 2) or
            (self.check_obstacle((self.pos_x - 1), self.pos_y, self.pos_z))

        )
        self.obstacle['w'] = (
            (self.pos_y == 2) or
            (self.check_obstacle(self.pos_x, (self.pos_y - 1), self.pos_z))
        )
        self.obstacle['s'] = (
            (self.pos_y == (self.game.southern_border - 1)) or
            (self.check_obstacle(self.pos_x, (self.pos_y + 1), self.pos_z))
        )

        if direction == 'd' and not self.obstacle['d']:
            self.set_prev()
            self.pos_x += 1
        elif direction == 'a' and not self.obstacle['a']:
            self.set_prev()
            self.pos_x -= 1
        elif direction == 'w' and not self.obstacle['w']:
            self.set_prev()
            self.pos_y -= 1
        elif direction == 's' and not self.obstacle['s']:
            self.set_prev()
            self.pos_y += 1
        else:
            return False

        return True

    def full_move(self):
        if self.choose_and_move():
            self.clear_prev()
            self.print_char()

    def lose_life(self, amount):
        self.health -= amount
        self.game.base_print_dialogue(
            '%s lost %s life.' % (self.name, self.health))

    def long_range_attack(self, _range, dmg, accuracy, attack_name):
        if not self.long_range_prepared:
            self.game.base_print_dialogue('Not prepared to use this weapon.')
            return
        self.game.base_print_dialogue('%s launched!' % attack_name)
        self.game.projectiles.append(
            Projectile(
                '.', self.player_input, _range, dmg, accuracy, attack_name,
                self.pos_x, self.pos_y
            )
        )
        self.long_range_prepared = False

    def attack(self, _range, dmg, accuracy, attack_name):
        self.get_things_in_range()
        hit = False
        for range_to_thing, thing in self.things_in_range:
            if hasattr(thing, 'health') and thing is not self:

                if range_to_thing <= _range:
                    accuracy_factor = 1
                else:
                    accuracy_factor = _range / range_to_thing

                thing.under_attack = True
                if random() < (accuracy * accuracy_factor) and thing.alive():
                    thing.health -= dmg
                    thing.show_hit()
                    hit = True
        if hit:
            self.game.base_print_dialogue(
                '%s succesfully %ss!' % (self.name, attack_name))
        else:
            self.game.base_print_dialogue(
                '%s tries to %s but misses!' % (self.name, attack_name))

    def get_things_in_range(self, max_range=5):
        self.things_in_range = []

        for x in range(-max_range, max_range + 1):
            for y in range(-max_range, max_range + 1):
                _range = abs(x) + abs(y)

                char = self.game.map.get(
                    (self.pos_x + x, self.pos_y + y)
                )

                self.things_in_range.append((_range, char))

    def alive(self):
        if self.dead:
            return False
        elif self.health <= 0:
            self.rep = 'X'
            self.game.base_print_dialogue('%s has died.' % self.name)
            self.dead = True
            self.print_char()
            return False
        return True


class Projectile(Creature):
    direct = {
        'i': ('w', 0, -1),
        'j': ('a', -1, 0),
        'k': ('s', 0, 1),
        'l': ('d', 1, 0)
    }

    def __init__(
            self, rep, direction, _range, dmg, accuracy, attack_name, pos_x,
            pos_y):
        Creature.__init__(self, game)
        self.rep = rep
        self.direction = direction
        self.pos_x = pos_x
        self.pos_y = pos_y
        self._range = _range
        self.dmg = dmg
        self.accuracy = accuracy
        self.attack_name = attack_name

    def die(self):
        self.dead = True
        try:
            thing = self.game.map.pop((self.pos_x, self.pos_y))
        except KeyError:
            thing = None

        if thing is self:
            self.rep = ' '
            self.print_char()

        else:
            self.game.map[(self.pos_x, self.pos_y)] = thing

    def be(self):
        if self.dead:
            return

        if self.direction in self.direct:
            real_direction, x_shift, y_shift = self.direct[self.direction]

            self._range -= 1
            if self._range <= 0:
                self.die()
                return
            target = self.game.map.get(
                (self.pos_x + x_shift, self.pos_y + y_shift)
            )
            if hasattr(target, 'health'):
                target.under_attack = True
                rando = random()
                if rando < self.accuracy and target.alive():
                    target.health -= self.dmg
                    target.show_hit()
                    self.game.base_print_dialogue('%s hit!' % self.attack_name)
                    self.die()
                elif rando >= self.accuracy:
                    self.game.base_print_dialogue('Oi! You missed!')
            else:
                if self.move_char(real_direction):
                    self.clear_prev()
                    self.print_char()
                else:
                    self.die()


class Player(Creature):
    VALID_REACTIONS = {'1', '2', '3', '4'}

    def __init__(self, game):
        Creature.__init__(self, game)
        self.long_range_prepared = False
        self.color = Fore.GREEN
        self.rep = 'A'
        self.print_char()
        self.player_input = None
        self.health = 100
        self.stamina = 100
        self.gold = 50
        self.experience = 0
        self.inventory = Inventory()
        self._actions = {
            '1': self.punch,
            '2': self.block,
            '3': self.dodge,
            'm': self.pickup,
        }

        self.items = [FlintandSteel(game)]

    @property
    def actions(self):
        current_actions = self._actions.copy()
        for item in self.items:
            current_actions.update(item.actions)
        return current_actions

    def get_player_input(self):
        self.player_input = getch()
        if self.player_input == 'q':
            os.system("stty echo")
            self.game.clear()
            sys.exit()

    def choose_and_move(self):
        if self.player_input in self.VALID_MOVES:
            return self.move_char(self.player_input)

    def action(self):
        if self.player_input in self.actions:
            self.actions[self.player_input]()

    def punch(self):
        self.attack(1, 2, .8, 'punch')

    def pickup(self):
        """Pickup all things next to player."""
        potential_items = []
        next_to = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for x, y in next_to:
            potential_items.append(
                self.game.map.get((self.pos_x + x, self.pos_y + y), None)
            )
        for item in potential_items:
            if isinstance(item, Item):
                self.items.append(item)
                item.player = self
                self.game.base_print(item.pos_x, item.pos_y, item.pos_z)
                self.game.base_print_dialogue('Picked up %s.' % item.name)

    def block(self):
        pass

    def dodge(self):
        pass


class Inventory(object):
    def __init__(self):
        self.pack = {}
        self.equipped = {
            'head': None,
            'torso': None,
            'legs': None,
            'feet': None,
            'left_hand': None,
            'right_hand': None,
        }
        self.pack_limit = 50
        self.equipped_limit = 50

    def show(self):
        pass


class Rat(Creature):
    def __init__(self, game):
        Creature.__init__(self, game)
        self.rep = 'r'
        self.pos_z = -2
        self.print_char()
        self.species = 'Rat'
        self.agression = 0

    def be(self):
        self.get_things_in_range()
        if self.alive():
            if not self.under_attack:
                self.full_move()
            else:
                my_range = 1
                attack = [0]
                # self.game.base_print_dialogue(self.things_in_range)
                for dist, thing in self.things_in_range:
                    if isinstance(thing, Player):
                        if dist <= (my_range + 1):
                            attack = [1, 0]
                        if dist <= my_range:
                            attack = [1]

                attack = sample(attack, 1)[0]

                if attack == 1:
                    self.attack(my_range, 1, .8, 'bite')
                else:
                    self.full_move()


class Game(object):
    ENCOUNTERS = []

    def __init__(self):
        self.get_size()
        self.clear()
        self.map = {}
        self.print_grass()
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

    def base_print(self, x, y, z, text=None, map_value=None):
        if z is None:
            raise ValueError('z cannot be None')
        if text and text != ' ':
            if (x, y) in self.map:
                if z not in self.map[(x, y)]:
                    self.map[(x, y)][z] = map_value or text
                elif z in self.map[(x, y)]:
                    raise EnvironmentError('Uncontrolled spacial collision.')
            else:
                self.map[(x, y)] = {z: map_value or text}
        elif text == ' ':
            self.map.get((x, y), {}).pop(z, None)

        text = self.get_map_text(x, y)

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
        # South Border
        for thing in range(self.eastern_border + 1):
            self.base_print(thing, self.southern_border, 5, 'x')
        # North Border
        for thing in range(self.eastern_border):
            self.base_print(thing, 1, 5, 'x')
        # East Border
        for thing in range(self.southern_border):
            self.base_print(self.eastern_border, thing, 5, 'x')
        # West Boarder
        for thing in range(self.southern_border - 2):
            self.base_print(1, thing + 2, 5, 'x')

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

    def print_grass(self):
        total_area = self.southern_border * self.eastern_border
        grass_count = randint(int(total_area*.02), int(total_area*.1))
        for blade in range(grass_count):
            rand = randint(0, 15)
            pos_z = 0
            if rand < 2 or len(self.map) == 0:
                pos_x = None
                pos_y = None
                # we want to generate this once, then keep trying until we get
                # fresh values
                while (pos_x, pos_y) in self.map or pos_x is None:
                    pos_x = randint(2, self.eastern_border - 1)
                    pos_y = randint(2, self.southern_border - 1)
            else:
                pos_x, pos_y = sample(self.map, 1)[0]
                while (pos_x, pos_y) in self.map:
                    nudge = randint(1, 4)
                    if nudge == 1 and pos_x < (self.eastern_border - 1):
                        pos_x += 1
                    elif nudge == 2 and pos_x > (2):
                        pos_x -= 1
                    elif nudge == 3 and pos_y < (self.southern_border - 1):
                        pos_y += 1
                    elif nudge == 4 and pos_y > (2):
                        pos_y -= 1

            # time.sleep(.003)
            self.base_print(pos_x, pos_y, pos_z, '#')

            pos_x = pos_y = pos_z = None

        # PRINT RIVER
        river = River(self)
        rand = randint(0, 1)
        # river starts on the east
        if rand:
            river.pos_x = self.eastern_border - 1
            river.pos_y = randint(2, self.southern_border - 1)
        # river starts on the north
        else:
            river.pos_x = randint(2, self.eastern_border - 1)
            river.pos_y = self.southern_border - 1

        while river.pos_x > 1 and river.pos_y > 1:
            river.print_char()
            if rand:
                river.pos_x -= 1
                river.pos_y += randint(-1, 1)
            else:
                river.pos_y -= 1
                river.pos_x += randint(-1, 1)

    def base_print_dialogue(self, dialogue):
        time_stamped_dialogue = '%s: %s' % (self.time, dialogue)
        for x in range(self.eastern_border):
            for y in range(self.southern_border + 1, self.rows + 1):
                self.base_print(x, y, 5, ' ')

        self.dialogue_history.append(time_stamped_dialogue)

        for ind, line in enumerate(self.dialogue_history[-5:]):
            self.base_print(1, self.southern_border + (1 + ind), 5, line)


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
        for col in range(self.western_border, self.game.columns):
            self.game.base_print(col, display_height, self.pos_z, ' ')
        self.game.map.get(
            (self.western_border, display_height), {}).pop(self.pos_z, None)
        self.game.base_print(
            self.western_border, display_height, self.pos_z, text)

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



game = Game()
game.run()
