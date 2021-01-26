# Unfinished

import simplegui
import math
import random

def load_image(url):
    return simplegui.load_image("https://i.imgur.com/" + url + ".png")

SCREEN_SIZE = [640, 480]
X = 0
Y = 1
Z = 2

PAUSE_BUTTON = load_image("vu9pqYR")

OBSTACLE1 = load_image("Tp2JknS")
OBSTACLE2 = load_image("OLIaVDA")

ENTITY_SHADOW = load_image("BSt9QJn")

PLAYER_DEFAULT = load_image("8UETpYE")
PLAYER_SIZE = [40, 40, 60]
PLAYER_DUCK_DIST = 10
PLAYER_DUCK_SIZE = [40, 40, 40]
PLAYER_HEALTH = 6
PLAYER_MANA = 6
PLAYER_DAMAGE = 0
PLAYER_PUSH = 0
PLAYER_PUSH_RES = 0
PLAYER_GRAVITY = 1
PLAYER_WALK_VEL = 6
PLAYER_DEACCEL = 1
PLAYER_JUMP_VEL = -11
PLAYER_DUCK_JUMP_VEL = -9

FIREBALL_DEFAULT = load_image("8UETpYE")
FIREBALL_DIST = 35
FIREBALL_SIZE = [30, 30, 30]
FIREBALL_HEALTH = 2
FIREBALL_DAMAGE = 5
FIREBALL_PUSH = 0
FIREBALL_PUSH_RES = 0
FIREBALL_GRAVITY = 1
FIREBALL_VEL = 10
FIREBALL_TIME = 60

EXPLOSION = load_image("8UETpYE")
EXPLOSION_DIST = 35
EXPLOSION_SIZE = [40, 40, 40]
EXPLOSION_HEALTH = 2
EXPLOSION_DAMAGE = 5
EXPLOSION_PUSH = 0
EXPLOSION_PUSH_RES = 0
EXPLOSION_GRAVITY = 0
EXPLOSION_VEL = 10
EXPLOSION_TIME = 15

BOMBARD_MANA_COST = 0
BOMBARD_COOLDOWN = 10

image_sizes = {PAUSE_BUTTON: [40, 40],
               OBSTACLE1: [800, 600],
               ENTITY_SHADOW: [1, 1],
               PLAYER_DEFAULT: [40, 120],
               FIREBALL_DEFAULT: [40, 120],
               EXPLOSION: [40, 120]}

axes = [1, 2, 3]

class Sprite():

    def __init__(self, image,
                 frames = 1):
        self.image = image
        self.size = image_sizes.get(image)
        self.frames = frames
        self.frame = 0
        self.is_animated = False
        if self.frames > 1:
            self.is_animated = True

    def get_center(self):
        return [self.size[X]/2 + self.frame * self.size[X],
                self.size[Y]/2]

    def update(self):
        if self.is_animated:
            self.frame += 1
            if self.frame >= self.frames:
                self.frame = 0

class Drawing():

    def __init__(self, sprite, position, size):
        self.sprite = sprite
        self.pos = position
        self.size = size

    def draw(self, canvas, position, size):
        canvas.draw_image(self.sprite.image,
                          self.sprite.get_center(),
                          self.sprite.size,
                          position,
                          size)

    def update(self):
        self.sprite.update()

class Panel(Drawing):

    def __init__(self, sprite, position, size,
                 can_click = False):
        super(Panel, self).__init__(sprite, position, size)
        self.can_click = can_click

    def set_function(self, function):
        self.click = function

    def is_clicked(self, mouse_pos):
        return (all(abs(self.pos[ax] - mouse_pos[ax]) <= self.size[ax]/2
                    for ax in range(axes[Y])))

    def draw(self, canvas):
        super(Panel, self).draw(canvas, self.pos, self.size)

class Object(Drawing):

    def __init__(self, sprite, position, size,
                 can_collide = False):
        super(Object, self).__init__(sprite, position, size)
        self.can_collide = can_collide
        self.is_active = True

    def __repr__(self):
        return "Object()"

    def __lt__(self, obj):
        if not self.get_dist(obj)[Z] < 0:
            return self.pos[Z] > obj.pos[Z]
        return self.pos[Y] < obj.pos[Y]

    def type_is(self, subclass):
        return isinstance(self, subclass)

    def get_draw_pos(self):
        return [self.pos[X] - camera.dist[X],
                self.pos[Y] + self.pos[Z] - camera.dist[Y]]

    def get_draw_size(self):
        return [self.size[X], self.size[Y] + self.size[Z]]

    def get_dist(self, obj):
        return [abs(self.pos[ax] - obj.pos[ax]) - self.size[ax]/2 - obj.size[ax]/2
                for ax in range(axes[Z])]

    def draw(self, canvas):
        super(Object, self).draw(canvas, self.get_draw_pos(), self.get_draw_size())

    def has_collided(self, obj):
        return all(dist < 0 for dist in self.get_dist(obj))

class Obstacle(Object):

    def __init__(self, drawing, position, size,
                 can_collide = True):
        super(Obstacle, self).__init__(drawing, position, size,
                                       can_collide)

    def __repr__(self):
        return "Obstacle()"

    def collide(self, obj):
        dist = self.get_dist(obj)
        axis = dist.index(max(dist))
        if self.pos[axis] < obj.pos[axis]:
            dist[axis] *= -1
        obj.pos[axis] += dist[axis]

        if axis == Z and dist[axis] < 0 and obj.type_is(Entity):
            obj.vel[Z] = 0
            obj.on_ground = True

class Entity(Object):

    def __init__(self, sprite, position, size,
                 velocity, health, damage,
                 push, push_resistance, gravity,
                 time = 0, face = 'down',
                 can_collide = True):
        super(Entity, self).__init__(sprite, position, size,
                                     can_collide)
        self.shadow = Object(Sprite(ENTITY_SHADOW),
                             [self.pos[X], self.pos[Y], 0],
                             [self.size[X], self.size[Y], 0])
        self.vel = velocity
        self.health = health
        self.damage = damage
        self.push_res = push_resistance
        self.push = push
        self.gravity = gravity
        self.time = time
        self.face = face
        self.on_ground = False

    def __repr__(self):
        return "Entity()"

    def collide(self, obj):
        if obj.type_is(Entity):
            obj.take_damage(self)

    def take_damage(self, obj):
        self.health -= obj.damage
        if self.health <= 0:
            self.is_active = False

    def get_pos(self, pos, dist, face):
        if face == 'left':
            return [pos[X] - dist, pos[Y], pos[Z]]
        elif face == 'right':
            return [pos[X] + dist, pos[Y], pos[Z]]
        elif face == 'up':
            return [pos[X], pos[Y] - dist, pos[Z]]
        elif face == 'down':
            return [pos[X], pos[Y] + dist, pos[Z]]

    def get_vel(self, vel, face):
        if face == 'left':
            return [-vel, 0, 0]
        elif face == 'right':
            return [vel, 0, 0]
        elif face == 'up':
            return [0, -vel, 0]
        elif face == 'down':
            return [0, vel, 0]

    def update(self):
        if not self.on_ground:
            self.vel[Z] += self.gravity
        self.on_ground = False
        if self.time > 0:
            self.time -= 1
        for ax in range(axes[Z]):
            self.pos[ax] += self.vel[ax]
        self.shadow.pos = [self.pos[X], self.pos[Y], 0]
        super(Entity, self).update()

class Player(Entity):

    def __init__(self, position):
        super(Player, self).__init__(Sprite(PLAYER_DEFAULT),
                                     position, PLAYER_SIZE,
                                     [0, 0, 0], PLAYER_HEALTH, PLAYER_DAMAGE,
                                     PLAYER_PUSH, PLAYER_PUSH_RES, PLAYER_GRAVITY)
        self.spells = [FieryBombardment(self)]
        """
        self.spells = [Slash(), Arrows(), Dash(), Fireball()]
        """
        self.mana = PLAYER_MANA
        self.selected_spell = 0
        self.holding_left = False
        self.holding_right = False
        self.holding_up = False
        self.holding_down = False
        self.walking_backwards = False
        self.holding_jump = False
        self.holding_duck = False
        self.ducking = False
        self.holding_cast = False

    def __repr__(self):
        return "Player()"

    def key_press(self, action):
        if action == 'left':
            self.holding_left = True
            if not self.holding_right:
                self.vel[X] = -PLAYER_WALK_VEL
            self.face = 'left'
        if action == 'right':
            self.holding_right = True
            if not self.holding_left:
                self.vel[X] = PLAYER_WALK_VEL
            self.face = 'right'
        if action == 'up':
            self.holding_up = True
            if not self.holding_down:
                self.vel[Y] = -PLAYER_WALK_VEL
            self.face = 'up'
        if action == 'down':
            self.holding_down = True
            if not self.holding_up:
                self.vel[Y] = PLAYER_WALK_VEL
            self.face = 'down'
        if action == 'duck':
            self.size = PLAYER_DUCK_SIZE
            self.pos[Z] += PLAYER_DUCK_DIST
            self.ducking = True
            self.holding_duck = True
        if action == 'jump':
            self.holding_jump = True
        if action == 'cast':
            self.holding_cast = True

    def key_release(self, action):
        if action == 'left':
            self.holding_left = False
            if self.holding_right:
                self.vel[X] = PLAYER_WALK_VEL
                self.face = 'right'
            else:
                self.vel[X] = 0
        if action == 'right':
            self.holding_right = False
            if self.holding_left:
                self.vel[X] = -PLAYER_WALK_VEL
                self.face = 'left'
            else:
                self.vel[X] = 0
        if action == 'up':
            self.holding_up = False
            if self.holding_down:
                self.vel[Y] = PLAYER_WALK_VEL
                self.face = 'down'
            else:
                self.vel[Y] = 0
        if action == 'down':
            self.holding_down = False
            if self.holding_up:
                self.vel[Y] = -PLAYER_WALK_VEL
                self.face = 'up'
            else:
                self.vel[Y] = 0
        if action == 'duck':
            self.size = PLAYER_SIZE
            self.pos[Z] -= PLAYER_DUCK_DIST
            self.ducking = False
            self.holding_duck = False
        if action == 'jump':
            self.holding_jump = False
        if action == 'cast':
            self.holding_cast = False

    def update(self):
        if self.ducking:
            for ax in range(axes[Y]):
                if abs(self.vel[ax]) == PLAYER_WALK_VEL:
                    self.vel[ax] /= 2

        if self.vel[X] < -PLAYER_WALK_VEL:
            if self.vel[X] + PLAYER_DEACCEL > -PLAYER_WALK_VEL:
                self.vel[X] = PLAYER_WALK_VEL
            else:
                self.vel[X] += PLAYER_DEACCEL
        if self.vel[X] > PLAYER_WALK_VEL:
            if self.vel[X] - PLAYER_DEACCEL < PLAYER_WALK_VEL:
                self.vel[X] = PLAYER_WALK_VEL
            else:
                self.vel[X] -= PLAYER_DEACCEL
        if self.vel[Y] < -PLAYER_WALK_VEL:
            if self.vel[Y] + PLAYER_DEACCEL > -PLAYER_WALK_VEL:
                self.vel[Y] = PLAYER_WALK_VEL
            else:
                self.vel[Y] += PLAYER_DEACCEL
        if self.vel[Y] > PLAYER_WALK_VEL:
            if self.vel[Y] - PLAYER_DEACCEL < PLAYER_WALK_VEL:
                self.vel[Y] = PLAYER_WALK_VEL
            else:
                self.vel[Y] -= PLAYER_DEACCEL

        if self.holding_jump and self.on_ground:
            if self.ducking:
                self.vel[Z] = PLAYER_DUCK_JUMP_VEL
            else:
                self.vel[Z] = PLAYER_JUMP_VEL

        if self.holding_duck and not self.ducking:
            self.size = PLAYER_DUCK_SIZE
            self.pos[Z] += PLAYER_DUCK_DIST
            self.ducking = True
        if not self.holding_duck and self.ducking:
            self.size = PLAYER_SIZE
            self.pos[Z] -= PLAYER_DUCK_DIST
            self.ducking = False

        if self.holding_cast and self.spells[self.selected_spell].mana_cost <= self.mana:
            if self.spells[self.selected_spell].time == 0:
                self.spells[self.selected_spell].cast()
        for spell in self.spells:
            spell.update()

        super(Player, self).update()

class Fireball(Entity):

    def __init__(self, position, face):
        super(Fireball, self).__init__(Sprite(FIREBALL_DEFAULT),
                                       self.get_pos(position, FIREBALL_DIST, face), FIREBALL_SIZE,
                                       self.get_vel(FIREBALL_VEL, face), FIREBALL_HEALTH, FIREBALL_DAMAGE,
                                       FIREBALL_PUSH, FIREBALL_PUSH_RES, FIREBALL_GRAVITY,
                                       FIREBALL_TIME, face)

    def explode(self):
        game.room.attacks.append(FireballExplosion(self.pos))
        self.is_active = False

    def collide(self, obj):
        self.explode()
        super(Fireball, self).collide(obj)

    def update(self):
        if self.time == 0:
            self.explode()
        super(Fireball, self).update()

class FireballExplosion(Entity):

    def __init__(self, position):
        super(FireballExplosion, self).__init__(Sprite(EXPLOSION),
                                                position, EXPLOSION_SIZE,
                                                [0, 0, 0], EXPLOSION_HEALTH, EXPLOSION_DAMAGE,
                                                EXPLOSION_PUSH, EXPLOSION_PUSH_RES, EXPLOSION_GRAVITY,
                                                EXPLOSION_TIME)

    def collide(self, obj):
        if obj.type_is(Obstacle):
            obj.collide(self)
        super(FireballExplosion, self).collide(obj)

    def update(self):
        if self.time == 0:
            self.is_active = False
        super(FireballExplosion, self).update()

class Spell():

    def __init__(self, caster, mana_cost, cooldown,
                 time = 0):
        self.caster = caster
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.time = time

    def cast(self):
        self.caster.mana -= self.mana_cost
        self.time += self.cooldown
        
    def update(self):
        if self.time > 0:
            self.time -= 1

class FieryBombardment(Spell):

    def __init__(self, caster):
        super(FieryBombardment, self).__init__(caster, BOMBARD_MANA_COST, BOMBARD_COOLDOWN)

    def cast(self):
        game.room.attacks.append(Fireball(self.caster.pos, self.caster.face))
        super(FieryBombardment, self).cast()

class Room():

    def __init__(self, position, size,
                 obstacles,
                 enemies = []):
        self.pos = position
        self.size = size
        self.obstacles = obstacles
        self.enemies = enemies
        self.attacks = []

class Map():

    def __init__(self, rooms):
        self.rooms = rooms

    def current_room(self):
        for room in self.rooms:
            if all(abs(room.pos[ax] - camera.pos[ax]) <= room.size[ax]/2
                   for ax in range(axes[Z])):
                return room

class Camera:

    def __init__(self):
        self.pos = [0, 0, -PLAYER_SIZE[Z]/2]

    def update(self):
        self.pos = [0, 0, 0]
        for ax in range(axes[Z]):
            for player in game.players:
                self.pos[ax] += player.pos[ax]
                if ax == Z and player.size == PLAYER_DUCK_SIZE:
                    self.pos[Z] -= PLAYER_DUCK_DIST
            self.pos[ax] /= len(game.players)
        self.dist = [self.pos[X] - SCREEN_SIZE[X]/2,
                     self.pos[Y] + self.pos[Z] - SCREEN_SIZE[Y]/2]

class Game:

    def start(self):
        self.panels = []
        self.create_panels()
        self.create_maps()
        self.map = self.get_map['hubworld']
        self.players = []
        self.create_player()
        self.is_paused = False

    def create_panels(self):
        pause_button = Panel(Sprite(PAUSE_BUTTON), [600, 40], [40, 40], True)
        pause_button.set_function(lambda: self.create_player())
        self.panels.append(pause_button)

    def create_player(self):
        self.players.append(Player(camera.pos))

    def create_maps(self):
        spawn = Room([0, 0, 0], [10000, 10000, 10000],
                     [Obstacle(Sprite(OBSTACLE1), [0, 0, 20], [800, 600, 40])])
        hubworld = Map([spawn])
        self.get_map = {'hubworld': hubworld}

    def get_player(self, number):
        if len(self.players) >= number:
            return self.players[number - 1]
        return self.players[0]

    def pause(self):
        if not self.is_paused:
            self.is_paused = True
        elif self.is_paused:
            self.is_paused = False

    def draw(self, screen):
        camera.update()

        self.room = self.map.current_room()
        self.room_objects = (self.players + [player.shadow for player in self.players]
                             + self.room.enemies + [enemy.shadow for enemy in self.room.enemies]
                             + self.room.attacks + [attack.shadow for attack in self.room.attacks]
                             + self.room.obstacles)
        self.room_objects.sort()
        for obj in self.room_objects:
            obj.draw(screen)
        for panel in self.panels:
            panel.draw(screen)

        if not self.is_paused:
            self.update()

    def update(self):
        for player in self.players:
            player.update()
        for enemy in self.room.enemies:
            enemy.update()
        for attack in self.room.attacks:
            attack.update()
        for panel in self.panels:
            panel.update()

        for obs in self.room.obstacles:
            for player in self.players:
                if obs.can_collide and player.can_collide:
                    if obs.has_collided(player):
                        obs.collide(player)
            for enemy in self.room.enemies:
                if obs.can_collide and enemy.can_collide:
                    if obs.has_collided(enemy):
                        obs.collide(enemy)

        for attack in self.room.attacks:
            for player in self.players:
                if attack.can_collide and player.can_collide:
                    if attack.has_collided(player):
                        attack.collide(player)
            for enemy in self.room.enemies:
                if attack.can_collide and enemy.can_collide:
                    if attack.has_collided(enemy):
                        attack.collide(enemy)
            for obs in self.room.obstacles:
                if attack.can_collide and obs.can_collide:
                    if attack.has_collided(obs):
                        attack.collide(obs)

        for enemy in self.room.enemies:
            if not enemy.is_active:
                self.room.enemies.remove(enemy)
        for attack in self.room.attacks:
            if not attack.is_active:
                self.room.attacks.remove(attack)
        for obs in self.room.obstacles:
            if not obs.is_active:
                self.room.obstacles.remove(obs)

    def mouse_click(self, mouse_pos):
        for panel in self.panels:
            if panel.can_click and panel.is_clicked(mouse_pos):
                panel.click()

    def key_press(self, key):
        if key == simplegui.KEY_MAP['a']:
            self.get_player(1).key_press('left')
        if key == simplegui.KEY_MAP['d']:
            self.get_player(1).key_press('right')
        if key == simplegui.KEY_MAP['w']:
            self.get_player(1).key_press('up')
        if key == simplegui.KEY_MAP['s']:
            self.get_player(1).key_press('down')
        if key == simplegui.KEY_MAP['f']:
            self.get_player(1).key_press('duck')
        if key == simplegui.KEY_MAP['g']:
            self.get_player(1).key_press('jump')
        if key == simplegui.KEY_MAP['h']:
            self.get_player(1).key_press('cast')

    def key_release(self, key):
        if key == simplegui.KEY_MAP['a']:
            self.get_player(1).key_release('left')
        if key == simplegui.KEY_MAP['d']:
            self.get_player(1).key_release('right')
        if key == simplegui.KEY_MAP['w']:
            self.get_player(1).key_release('up')
        if key == simplegui.KEY_MAP['s']:
            self.get_player(1).key_release('down')
        if key == simplegui.KEY_MAP['f']:
            self.get_player(1).key_release('duck')
        if key == simplegui.KEY_MAP['g']:
            self.get_player(1).key_release('jump')
        if key == simplegui.KEY_MAP['h']:
            self.get_player(1).key_release('cast')

camera = Camera()
game = Game()
game.start()

frame = simplegui.create_frame("",
                               SCREEN_SIZE[X],
                               SCREEN_SIZE[Y])
frame.set_mouseclick_handler(game.mouse_click)
frame.set_keydown_handler(game.key_press)
frame.set_keyup_handler(game.key_release)
frame.set_draw_handler(game.draw)

frame.start()
