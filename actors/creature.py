import os
import sys
import time
from random import sample, random
from colorama import Fore
from .item import FlintandSteel, Item
from .spell import RingOfFire
from .biome import Biome
from utils import all_names, getch


class Creature(object):
    VALID_MOVES = {'a', 'w', 's', 'd'}

    def __init__(self, game, my_map=None):
        self.obstacle = {
            'w': False,
            'wd': False,
            'd': False,
            'ds': False,
            's': False,
            'sa': False,
            'a': False,
            'aw': False,
        }
        self.direction_map = {
            # direction: [x,y],
            'w': [0, -1],
            'wd': [1, -1],
            'd': [1, 0],
            'ds': [1, 1],
            's': [0, 1],
            'sa': [-1, 1],
            'a': [-1, 0],
            'aw': [-1, -1],
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
        self.prev_direction = None
        self.prev_map = None
        self.health = 10
        self.name = sample(all_names, 1)[0]
        self.under_attack = False
        self.dead = False
        self.my_map = my_map or game.map

    def set_map_value(self):
        self.game.set_map_value(self.pos_x, self.pos_y, self.pos_z, None, self.my_map)
        if not self.dead:
            self.game.set_map_value(self.pos_x, self.pos_y, self.pos_z, self, self.my_map)
        else:
            self.game.print_intersection(self.pos_x, self.pos_y)

    def print_char(self):
        self.set_map_value()
        self.game.print_intersection(self.pos_x, self.pos_y)

    def show_hit(self):
        main_color = self.color
        self.color = Fore.RED
        self.print_char()
        time.sleep(.15)
        self.color = main_color
        self.print_char()

    def clear_prev(self):
        # convenience mappings
        x = self.prev_pos_x
        y = self.prev_pos_y
        z = self.prev_pos_z

        this_map = self.prev_map or self.my_map
        self.prev_map = None
        # if the thing in your previous space is you
        if this_map.get((x, y), {}).get(z, None) is self:
            # then delete your old self
            self.game.set_map_value(x, y, z, None, this_map)

        # otherwise, print the top thing where you used to be

        self.game.print_intersection(x, y, target_map=this_map)

    def set_prev(self):
        self.prev_pos_x = self.pos_x
        self.prev_pos_y = self.pos_y
        self.prev_pos_z = self.pos_z
        self.prev_direction = self.direction

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
        try:
            map_value = self.game.map[(x, y)][z]
        except KeyError:
            # if it's not in the map, its not an obstacle
            return False

        # otherwise it is
        return map_value

    def collide_dialogue(self, target):
        pass

    def move_char(self, direction):
        # putting this here because it is used in set_prev,
        # probably not the best place
        self.direction = direction

        x_shift, y_shift = self.direction_map[self.direction]
        new_x = self.pos_x + x_shift
        new_y = self.pos_y + y_shift

        # TODO: cleanup here
        # Eastern Border
        if new_x == self.game.eastern_border:
            new_x = 2
            map_x, map_y = self.game.current_map
            self.game.get_map(map_x + 1, map_y)
            self.prev_map = self.my_map
            self.my_map = self.game.map

        # Western Border
        elif new_x == 1:
            new_x = self.game.eastern_border - 1
            map_x, map_y = self.game.current_map
            self.game.get_map(map_x - 1, map_y)
            self.prev_map = self.my_map
            self.my_map = self.game.map

        # Southern Border
        elif new_y == self.game.southern_border:
            new_y = 2
            map_x, map_y = self.game.current_map
            self.game.get_map(map_x, map_y + 1)
            self.prev_map = self.my_map
            self.my_map = self.game.map

        # Northern Border
        elif new_y == 1:
            new_y = self.game.southern_border - 1
            map_x, map_y = self.game.current_map
            self.game.get_map(map_x, map_y - 1)
            self.prev_map = self.my_map
            self.my_map = self.game.map

        self.obstacle[self.direction] = (
            self.check_obstacle(new_x, new_y, self.pos_z)
        )

        if not self.obstacle[self.direction]:
            self.set_prev()
            self.pos_x = new_x
            self.pos_y = new_y
            return True
        else:
            self.collide_dialogue(self.obstacle[self.direction])
            return False

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
                self.game, '.', self.player_input, _range, dmg, accuracy,
                attack_name, self.pos_x, self.pos_y
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

                z_dict = self.game.map.get(
                    (self.pos_x + x, self.pos_y + y), {}
                )

                for char in z_dict.values():
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
            self, game, rep, direction, _range, dmg, accuracy, attack_name, pos_x,
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
        self.print_char()

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


class SentientVine(Projectile):
    def be(self):
        self.health -= 1
        if self.health <= 0:
            self.die()

        vine_movement = {
            'w': ['w', 'wd', 'aw'],
            'wd': ['wd', 'w', 'd'],
            'd': ['wd', 'd', 'ds'],
            'ds': ['ds', 'd', 's'],
            's': ['s', 'ds', 'sa'],
            'sa': ['sa', 's', 'a'],
            'a': ['a', 'sa', 'aw'],
            'aw': ['aw', 'a', 'w'],
            None: ['a', 'w', 'd', 's']
        }

        if self.dead:
            return


        move_set = vine_movement[self.prev_direction]

        direction = sample(move_set, 1)[0]

        x_shift, y_shift = self.direction_map[direction]

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
            if self.move_char(direction):
                from random import randint
                # self.clear_prev()
                self.print_char()
                # if randint(1, 4) == 3:
                if True:
                    self.game.vines.append(
                        SentientVine(
                            self.game, 'o', 'w', 10, 1, 1, 'attack_name',
                            self.pos_x, self.pos_y + 1
                        )
                    )
            else:
                self.die()



class Player(Creature):
    VALID_REACTIONS = {'1', '2', '3', '4'}

    def __init__(self, game):
        Creature.__init__(self, game)
        self.long_range_prepared = False
        self.color = Fore.MAGENTA
        self.rep = 'A'
        self.print_char()
        self.player_input = None
        self.waiting_for_input = None
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
            # 'v': self.create_vine
        }

        self.items = [FlintandSteel(game)]
        self.spells = [RingOfFire(game)]

    def action(self):
        if self.player_input in self.actions:
            self.actions[self.player_input]()

    @property
    def actions(self):
        current_actions = self._actions.copy()
        for item in self.items:
            current_actions.update(item.actions)
        for spell in self.spells:
            current_actions.update(spell.actions)
        return current_actions

    def choose_and_move(self):
        if self.player_input in self.VALID_MOVES:
            return self.move_char(self.player_input)

    def collide_dialogue(self, target):
        # if isinstance(target, Border):
        #     self.game.base_print_dialogue('The end of the world.')
        # else:
        self.game.base_print_dialogue(
            'A collision has occurred with %s.' % target)

    def create_vine(self):
        self.game.vines.append(SentientVine(
            self.game, 'o', 'w', 10, 1, 1, 'attack_name', self.pos_x,
            self.pos_y + 1)
        )

    def block(self):
        pass

    def dodge(self):
        pass

    def get_player_input(self):
        self.player_input = getch()
        self.waiting_for_input = False

    def pickup(self):
        """Pickup all things next to player."""
        potential_items = []
        next_to = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for x, y in next_to:
            z_dict = self.game.map.get((self.pos_x + x, self.pos_y + y), {})
            potential_items.extend(z_dict.values())
        for item in potential_items:
            if isinstance(item, Item):
                self.items.append(item)
                item.player = self
                self.game.set_map_value(item.pos_x, item.pos_y, item.pos_z, None, self.my_map)
                self.game.base_print_dialogue('Picked up %s.' % item.name)

    def punch(self):
        self.attack(1, 2, .8, 'punch')


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
        self.pos_z = 10
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
