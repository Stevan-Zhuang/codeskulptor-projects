# An old game made for the Programming 11 course at FPSS
# by Stevan Zhuang

# TODO:
# Add ending so game doesn't crash on completion
# Add python 3 compatibility

import simplegui, random

DIMENSIONS = [760, 600]
SCALE = 40

class Object:
    
    def __init__(self, position):
        self.active = True
        self.origin = [position[0], position[1]]
        self.pos = [position[0], position[1]]
    
    def will_collide(obs, ent, axis):
        # Obstacle against entity collision check
        other_axis = abs(axis-1)
        total_size = [ent.size[0] + obs.size[0],
                      ent.size[1] + obs.size[1]]
        future_pos = [ent.pos[0] + ent.vel[0],
                      ent.pos[1] + ent.vel[1]]
        # If entity will be on the same level as onject
        if abs(future_pos[other_axis] - obs.pos[other_axis]) < total_size[other_axis]:
            # Return if entity will collide
            return ((ent.pos[axis] - obs.pos[axis] >= total_size[axis] and
                     future_pos[axis] - obs.pos[axis] <= total_size[axis]) or
                    (obs.pos[axis] - ent.pos[axis] >= total_size[axis] and
                     obs.pos[axis] - future_pos[axis] <= total_size[axis]))
    
    def has_collided(thing, ent):
        # Item / Entity against entity collision check
        total_size = [ent.size[0] + thing.size[0],
                      ent.size[1] + thing.size[1]]
        if thing.active and ent.active:
            # Return if is colliding
            return (abs(ent.pos[0] - thing.pos[0]) <= total_size[0]
                and abs(ent.pos[1] - thing.pos[1]) <= total_size[1])

class Image:
    BACKGROUND = simplegui.load_image('https://i.imgur.com/9DkzQ8E.png')
    ROOM_0 = simplegui.load_image('https://i.imgur.com/cuF1LbG.png')
    ROOM_1 = simplegui.load_image('https://i.imgur.com/2Uq5M0S.png')
    ROOM_2 = simplegui.load_image('https://i.imgur.com/OFcVDso.png')
    ROOM_2_1 = simplegui.load_image('https://i.imgur.com/LLqbVM0.png')
    ROOM_3 = simplegui.load_image('https://i.imgur.com/cqlYyhP.png')
    ROOM_3_1 = simplegui.load_image('https://i.imgur.com/5Wb05Oe.png')
    ROOM_4 = simplegui.load_image('https://i.imgur.com/b9TCKJI.png')
    ROOM_4_1 = simplegui.load_image('https://i.imgur.com/U3mFgk0.png')

    def __init__(self, image, position, size):
        self.image = image
        self.origin = [position[0], position[1]]
        self.s_pos = [position[0], position[1]]
        self.size = size
        
    def draw(self, canvas):
        canvas.draw_image(self.image,
                         (self.size[0], self.size[1]),
                         (self.size[0] * 2, self.size[1] * 2),
                         (self.s_pos[0], self.s_pos[1]),
                         (self.size[0] * 2.5, self.size[1] * 2.5))
        
    def on_screen(self):
        return (-self.size[0] < self.s_pos[0] < DIMENSIONS[0] + self.size[0]
        and -self.size[1] < self.s_pos[1] < DIMENSIONS[1] + self.size[1])
        
class Spritesheet:
    def __init__(self, sheet, speed, columns, rows):
        self.sheet = sheet
        self.speed = speed
        self.col = columns
        self.row = rows
        
class Animation(Image):
    NONE = Spritesheet(simplegui.load_image(''),1,1,1)
    def __init__(self, image, position, size):
        Image.__init__(self, image, position, size)
        self.a_time = 0
        self.a_counter = 0
        
    def draw(self, canvas):
        sheet_loc = (self.size[0] + self.a_time % self.image.col * self.size[0]*2,
                     self.size[1] + self.a_time // self.image.col * self.size[1]*2)
        canvas.draw_image(self.image.sheet,
                         (sheet_loc),
                         (self.size[0] * 2, self.size[1] * 2),
                         (self.s_pos[0], self.s_pos[1]),
                         (self.size[0] * 2.5, self.size[1] * 2.5))
        
    def animation_update(self):
        self.a_counter += 1
        if self.a_counter%self.image.speed == 0: 
            self.a_time += 1
            self.a_time %= self.image.col*self.image.row
            
    def reset_animation(self):
        self.a_time = 0
        self.a_counter = 0

class Obstacle(Object):
    # Things that interact with the player by stopping them
    def __init__(self, position):
        Object.__init__(self, position)
        self.size = [SCALE/2,SCALE/2]

    def check_collision(self):
        # Checks collision against player and all entities
        for axis in range(2):
            if self.will_collide(player, axis): self.collision(player, axis)
            for ent in Game.room(0,0).ents:
                if self.will_collide(ent, axis): self.collision(ent, axis)
        
    def stop(self, ent, axis):
        # Stops entity movement against obstacle
        total_size = [ent.size[0] + self.size[0],
                      ent.size[1] + self.size[1]]
        if ent.pos[axis] - self.pos[axis] > 0: # Left or up collision
            ent.vel[axis] = self.pos[axis] - ent.pos[axis] + total_size[axis]
        elif ent.pos[axis] - self.pos[axis] < 0: # Right or down collision
            ent.vel[axis] = self.pos[axis] - ent.pos[axis] - total_size[axis]
            
    def on_screen(self):
        cam_dist = [abs(DIMENSIONS[0]/2 - player.s_pos[0] + self.size[0]),
                    abs(DIMENSIONS[1]/2 - player.s_pos[1] + self.size[1])]
        return (abs(self.pos[0] - player.pos[0]) < DIMENSIONS[0] + cam_dist[0]
            and abs(self.pos[1] - player.pos[1]) < DIMENSIONS[1] + cam_dist[1])

class Block(Obstacle):
    # Ordinary obstacle
    def collision(self, ent, axis):
        if axis == 1 and ent.pos[1] < self.pos[1]:
            ent.on_ground(self)
        self.stop(ent, axis)

class Platform(Obstacle):
    # Entities will only collide downwards
    def collision(self, ent, axis):
        if axis == 1 and ent.pos[1] < self.pos[1]:
            ent.on_ground(self)
            self.stop(ent, axis)

class Hazard(Obstacle):
    # Kills entities
    dmg = 100
    def collision(self, ent, axis):
        ent.take_damage(self)
        self.stop(ent, axis)

class Entity(Object, Animation):
    # Things that can act by themselves
    
    def __init__(self, image, position, size, health):
        Object.__init__(self, position)
        Animation.__init__(self, image, position, size)
        self.max_hp = health
        self.hp = health
        self.ground = False
        self.d_vel = [0, 0]
        self.a_vel = [0, 0]
        self.vel = [0, 0]
        self.time = random.randrange(50)
        self.i_time = 0
        
    def check_velocity(self):
        pass
        
    def velocity_update(self):
        if not self.ground:
            if self.a_vel[1] + Game.GRAVITY > Game.GRAVITY_MAX:
                self.a_vel[1] = Game.GRAVITY_MAX
            else: self.a_vel[1] += Game.GRAVITY
        for axis in range(2):
            self.vel[axis] = self.d_vel[axis] + self.a_vel[axis]
        if self.ground and not self.ground.will_collide(self, 1):
            self.ground = False
        
    def check_collision(self):
        # Checks collision against player
        if self.has_collided(player):
            self.collision(player)
            
    def collision(self, ent):
        pass
            
    def on_ground(self, obs):
        if isinstance(self, Character): self.dash = True
        self.ground = obs
        self.a_vel[1] = 0
        
    def update(self):
        # add velocity to entity position
        for axis in range(2): 
            self.pos[axis] += self.vel[axis]
            self.s_pos[axis] += self.vel[axis]
        if self.time > 0: self.time -= 1
        if self.i_time > 0: self.i_time -= 1
        self.check_animation()
        self.animation_update()
        
    def take_damage(self, thing):
        if self.i_time == 0:
            self.hp -= thing.dmg
            if self.hp <= 0 and self.active: # Death
                self.active = False
                self.time = Game.DEATH_TIME
                self.image = self.DEATH
                self.reset_animation()
            else: self.i_time = Game.INVIN_TIME
            
class Character(Entity):
    
    IDLE_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/eQ2pwZu.png'),1,1,1)
    IDLE_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/RtW1ehI.png'),1,1,1)
    WALK_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/Q3XPWm7.png'),3,3,2)
    WALK_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/tybqtOk.png'),3,3,2)
    FALL_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/iSpX1Bb.png'),1,1,1)
    FALL_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/10laCDh.png'),1,1,1)
    ROLL_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/hIHrOsI.png'),3,3,3)
    ROLL_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/v557jzv.png'),3,3,3)
    LUNGE_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/tha6h5l.png'),3,3,3)
    LUNGE_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/6vHaznZ.png'),3,3,3)
    DAMAGED_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/vT65ViB.png'),2,2,1)
    DAMAGED_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/0G1gmyM.png'),2,2,1)
    DEATH_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/utQIy0c.png'),4,5,4)
    DEATH_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/akinEb2.png'),4,5,4)
    
    def __init__(self, weapon, image, position, size, health):
        Entity.__init__(self, image, position, size, health)
        self.weapon = weapon
        self.dmg = self.weapon.dmg
        self.h_right = False
        self.h_left = False
        self.dash = False
        self.face = 'right'
        self.spawn = 'left'
        self.time = 0
        
    def draw(self, canvas):
        sheet_loc = (self.size[0]*3 + self.a_time % self.image.col * self.size[0]*6,
                     self.size[1]*3 + self.a_time // self.image.col * self.size[1]*6)
        canvas.draw_image(self.image.sheet,
                         (sheet_loc),
                         (self.size[0]*6, self.size[1]*6),
                         (self.s_pos[0], self.s_pos[1]),
                         (self.size[0]*7.5, self.size[1]*7.5))
        if self.weapon.active: self.weapon.draw(canvas)

    def key_down(self, key):
        if key == simplegui.KEY_MAP['right']: # Move right / Aim dash right
            self.h_right = True
            self.d_vel[0] += Game.WALK_VEL
            if not self.h_left: self.face = 'right'
        if key == simplegui.KEY_MAP['left']: # Move left / Aim dash left
            self.h_left = True
            self.d_vel[0] -= Game.WALK_VEL
            if not self.h_right: self.face = 'left'
                
        if key == simplegui.KEY_MAP['e']: # Dash
            if self.time <= Game.MOVE_USAGE and self.dash:
                if self.h_right and not self.h_left:
                    self.dash = False
                    self.time = Game.DASH_COOLDOWN
                    self.i_time = Game.DASH_INVIN
                    self.reset_animation()
                    if self.ground:
                        self.a_vel[0] = Game.DASH_ACCEL[0]
                        self.image = self.ROLL_RIGHT
                    else:
                        self.a_vel = [Game.DASH_ACCEL[0], Game.DASH_ACCEL[1]]
                        self.image = self.LUNGE_RIGHT
                elif self.h_left and not self.h_right:
                    self.dash = False
                    self.time = Game.DASH_COOLDOWN
                    self.i_time = Game.DASH_INVIN
                    self.reset_animation()
                    if self.ground:
                        self.a_vel[0] = -Game.DASH_ACCEL[0]
                        self.image = self.ROLL_LEFT
                    else:
                        self.a_vel = [-Game.DASH_ACCEL[0], Game.DASH_ACCEL[1]]
                        self.image = self.LUNGE_LEFT
                        
        if key == simplegui.KEY_MAP['f']: # Attack
            if self.time <= Game.MOVE_USAGE and self.weapon.time <= Game.MOVE_USAGE:
                self.a_vel[0] = 0
                self.weapon.reset_animation()
                self.weapon.active = True
                if self.face == 'right':
                    self.weapon.image = self.weapon.RIGHT
                    self.weapon.set_pos(60)
                elif self.face == 'left':
                    self.weapon.image = self.weapon.LEFT
                    self.weapon.set_pos(-60)
                self.weapon.time = Game.ATTACK_DURATION

        if key == simplegui.KEY_MAP['space']: # Jump
            if self.ground and self.time <= Game.MOVE_USAGE:
                self.a_vel[1] = Game.JUMP_ACCEL - abs(self.a_vel[0]/2)
                self.time = Game.JUMP_COOLDOWN
                
    def key_up(self,key):
        if key == simplegui.KEY_MAP['right']: # Stop moving right
            self.d_vel[0] -= Game.WALK_VEL
            if self.h_left: self.face = 'left'
            self.h_right = False
                
        if key == simplegui.KEY_MAP['left']: # Stop moving left
            self.d_vel[0] += Game.WALK_VEL
            if self.h_right: self.face = 'right'
            self.h_left = False
            
    def check_velocity(self):
        if self.active:
            # Deacceleration when past max speed
            if self.a_vel[0] > Game.WALK_ACCEL_MAX:
                if self.a_vel[0] - Game.DEACCEL_MAX < Game.WALK_ACCEL_MAX:
                    self.a_vel[0] = Game.WALK_ACCEL_MAX
                else: self.a_vel[0] -= Game.DEACCEL_MAX
            elif self.a_vel[0] < -Game.WALK_ACCEL_MAX:
                if self.a_vel[0] + Game.DEACCEL_MAX > -Game.WALK_ACCEL_MAX:
                    self.a_vel[0] = -Game.WALK_ACCEL_MAX
                else: self.a_vel[0] += Game.DEACCEL_MAX
            # Going both directions deacceleration
            if self.h_right and self.h_left:
                if self.a_vel[0] > Game.WALK_DEACCEL_MAX:
                    if self.a_vel[0] - Game.WALK_DEACCEL < Game.WALK_DEACCEL_MAX:
                        self.a_vel[0] = Game.WALK_DEACCEL_MAX
                    else: self.a_vel[0] -= Game.WALK_DEACCEL
                if self.a_vel[0] < Game.WALK_DEACCEL_MAX:
                    if self.a_vel[0] + Game.WALK_DEACCEL > Game.WALK_DEACCEL_MAX:
                        self.a_vel[0] = Game.WALK_DEACCEL_MAX
                    else: self.a_vel[0] += Game.WALK_DEACCEL
            # Hold right acceleration
            if self.h_right and self.a_vel[0] <= Game.WALK_ACCEL_MAX:
                if self.a_vel[0] + Game.WALK_ACCEL > Game.WALK_ACCEL_MAX:
                    self.a_vel[0] = Game.WALK_ACCEL_MAX
                else: self.a_vel[0] += Game.WALK_ACCEL
            # Release right deacceleration
            elif self.a_vel[0] > Game.WALK_DEACCEL_MAX:
                if self.a_vel[0] - Game.WALK_DEACCEL < Game.WALK_DEACCEL_MAX:
                    self.a_vel[0] = Game.WALK_DEACCEL_MAX
                else: self.a_vel[0] -= Game.WALK_DEACCEL
            # Hold left acceleration
            if self.h_left and self.a_vel[0] >= -Game.WALK_ACCEL_MAX:
                if self.a_vel[0] - Game.WALK_ACCEL < -Game.WALK_ACCEL_MAX: 
                    self.a_vel[0] = -Game.WALK_ACCEL_MAX
                else: self.a_vel[0] -= Game.WALK_ACCEL
            # Release left deacceleration
            elif self.a_vel[0] < Game.WALK_DEACCEL_MAX:
                if self.a_vel[0] + Game.WALK_DEACCEL > Game.WALK_DEACCEL_MAX:
                    self.a_vel[0] = Game.WALK_DEACCEL_MAX
                else: self.a_vel[0] += Game.WALK_DEACCEL
            self.velocity_update()
        else: self.vel = [0, 0]
            
    def check_collision(self):
        self.weapon.check_collision()
        
    def update(self):
        # add velocity to player position
        for axis in range(2):
            self.pos[axis] += self.vel[axis]
        if self.time > 0: self.time -= 1
        if self.i_time > 0: self.i_time -= 1
        self.check_animation()
        self.animation_update()
        self.weapon.update()
        
    def check_animation(self):
        if self.active and self.time == 0:
            if self.ground:
                if self.vel[0] == 0:
                    if self.face == 'left': self.image = self.IDLE_LEFT
                    elif self.face == 'right': self.image = self.IDLE_RIGHT
                else:
                    if self.face == 'left' and self.image != self.WALK_LEFT:
                        self.image = self.WALK_LEFT
                        self.reset_animation()
                    elif self.face == 'right' and self.image != self.WALK_RIGHT:
                        self.image = self.WALK_RIGHT
                        self.reset_animation()
            else:
                if self.face == 'left': self.image = self.FALL_LEFT
                elif self.face == 'right': self.image = self.FALL_RIGHT
            
    def take_damage(self, thing):
        if self.i_time == 0:
            self.hp -= thing.dmg
            if self.hp <= 0: # Death
                if self.active:
                    self.active = False
                    self.time = Game.RESPAWN_COOLDOWN
                    if self.face == 'left': self.image = self.DEATH_LEFT
                    elif self.face == 'right': self.image = self.DEATH_RIGHT
                    self.reset_animation()
            else:
                self.a_vel[1] = -Game.KNOCKBACK_ACCEL
                if self.pos[0] < thing.pos[0]:
                    self.a_vel[0] = -Game.KNOCKBACK_ACCEL
                    self.image = self.DAMAGED_LEFT
                elif self.pos[0] > thing.pos[0]:
                    self.a_vel[0] = Game.KNOCKBACK_ACCEL
                    self.image = self.DAMAGED_RIGHT
                self.time = Game.INVIN_TIME
                self.i_time = Game.INVIN_TIME
                self.reset_animation()

            
    def respawn(self):
        # Respawns the player at last room entry point
        if player.time <= Game.DEATH_TIME:
            if self.face == 'left': self.image = self.IDLE_LEFT
            elif self.face == 'right': self.image = self.IDLE_RIGHT
            self.active = True
            self.ground = False
            self.dash = False
            self.pos = [self.origin[0], self.origin[1]]
            self.a_vel = [0, 0]
            self.time = 0
            self.i_time = 0
            self.a_time = 0
            Game.reset_room()
            Camera.respawn()
        
class Weapon(Object, Animation):
    LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/hsPnQre.png'),2,5,2)
    RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/Mhi3Tij.png'),2,5,2)
    def __init__(self, image, position, size, damage):
        Object.__init__(self, position)
        Animation.__init__(self, image, position, size)
        self.dmg = damage
        self.active = False
        self.time = 0

    def check_collision(self):
        # Checks collision against all entities
        for ent in Game.room(0,0).ents:
            if self.has_collided(ent):
                self.collision(ent)
                                
    def collision(self, ent):
        ent.take_damage(player)
        
    def update(self):
        if self.time == 0: self.active = False
        elif self.time > 0: self.time -= 1
        self.animation_update()
        
    def set_pos(self,dist):
        self.pos = [player.pos[0] + dist, player.pos[1]]
        self.s_pos = [player.s_pos[0] + dist, player.s_pos[1]]
            
class Helper(Entity):
    LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/Ss9cCgL.png'),1,1,1)
    RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/L19pOI2.png'),1,1,1)
    DEATH = Spritesheet(simplegui.load_image('https://i.imgur.com/Q2DgJIY.png'),2,5,2)
    def check_animation(self):
        if self.active:
            if player.pos[0] < self.pos[0]: self.image = self.LEFT
            elif player.pos[0] > self.pos[0]: self.image = self.RIGHT
        elif self.time == 0: self.image = self.NONE

class Slime(Entity):
    DEFAULT = Spritesheet(simplegui.load_image('https://i.imgur.com/ZsOOGhw.png'),2,2,2)
    INVUN = Spritesheet(simplegui.load_image('https://i.imgur.com/t3dwdRf.png'),2,2,2)
    DEATH = Spritesheet(simplegui.load_image('https://i.imgur.com/Q2DgJIY.png'),2,5,2)
    def __init__(self, picture, position, size, health):
        Entity.__init__(self, picture, position, size, health)
        self.dmg = 1

    def check_velocity(self):
        if self.active: # Enemy A.I.
            if self.time == 0:
                self.time = 100
                self.a_vel[1] = Game.SLIME_JUMP_ACCEL
                if player.pos[0] > self.pos[0]: self.d_vel[0] = Game.SLIME_WALK_VEL
                elif player.pos[0] < self.pos[0]: self.d_vel[0] = -Game.SLIME_WALK_VEL
            elif self.ground: self.d_vel[0] = 0
            self.velocity_update()
        else: self.vel = [0, 0]
            
    def collision(self, ent):
        ent.take_damage(self)
        
    def check_animation(self):
        if self.active:
            if self.i_time > 0: self.image = self.INVUN
            else: self.image = self.DEFAULT
        elif self.time == 0: self.image = self.NONE

class Big_Slime(Slime):
    DEFAULT = Spritesheet(simplegui.load_image('https://i.imgur.com/Bf07dbp.png'),2,2,2)
    INVUN = Spritesheet(simplegui.load_image('https://i.imgur.com/5uyS3Lf.png'),2,2,2)
    DEATH = Spritesheet(simplegui.load_image('https://i.imgur.com/kCEuknr.png'),2,5,2)

class Crawler(Entity):
    LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/Ie5Qwki.png'),2,4,4)
    RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/K76ES2Z.png'),2,4,4)
    INVUN_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/iIL9OmB.png'),2,4,4)
    INVUN_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/hjSAIXE.png'),2,4,4)
    DEATH = Spritesheet(simplegui.load_image('https://i.imgur.com/tL3eKKE.png'),2,5,2)
    def __init__(self, picture, position, size, health):
        Entity.__init__(self, picture, position, size, health)
        self.dmg = 1
        if player.pos[0] > self.pos[0]: self.d_vel[0] = -Game.CRAWLER_WALK_VEL
        elif player.pos[0] < self.pos[0]: self.d_vel[0] = Game.CRAWLER_WALK_VEL
    
    def check_velocity(self):
        if self.active: # Enemy A.I.
            if self.vel[0] == 0: self.d_vel[0] *= -1
            self.velocity_update()
        else: self.vel = [0, 0]
            
    def collision(self, ent):
        ent.take_damage(self)
        
    def check_animation(self):
        if self.active:
            if self.i_time > 0:
                if self.vel[0] < 0: self.image = self.INVUN_LEFT
                elif self.vel[0] > 0: self.image = self.INVUN_RIGHT
            elif self.vel[0] < 0: self.image = self.LEFT
            elif self.vel[0] > 0: self.image = self.RIGHT
        elif self.time == 0: self.image = self.NONE
            
class Big_Crawler(Crawler):
    LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/FWf3COa.png'),2,4,4)
    RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/Uygy5sl.png'),2,4,4)
    INVUN_LEFT = Spritesheet(simplegui.load_image('https://i.imgur.com/AVzJcjx.png'),2,4,4)
    INVUN_RIGHT = Spritesheet(simplegui.load_image('https://i.imgur.com/9Xbo7Nk.png'),2,4,4)
    DEATH = Spritesheet(simplegui.load_image('https://i.imgur.com/zsTk6Et.png'),2,5,2)

class Camera:
    # Scrolls the screen and controls room changes
    
    def check_collision(ent, axis):
        # Stops player from going off edge of screen
        future_pos = ent.pos[axis] + ent.vel[axis]
        if future_pos <= -Game.ROOM_BOUND:
            ent.vel[axis] = -ent.pos[axis] - Game.ROOM_BOUND
        elif future_pos >= Game.room(0,0).bounds[axis] + Game.ROOM_BOUND:
            ent.vel[axis] = Game.room(0,0).bounds[axis] - ent.pos[axis] + Game.ROOM_BOUND
    
    def shift(axis):
        # Moves the screen when player moves
        future_pos = player.pos[axis] + player.vel[axis] # Player position after velocity
        # Camera boundaries
        bound_1 = DIMENSIONS[axis]/2 # Left / Up
        bound_2 = Game.room(0,0).bounds[axis] - DIMENSIONS[axis]/2 # Right / Down
        
        # If will go into left / up boundary
        if future_pos < bound_1:
            if player.pos[axis] > bound_1: # If not already in boundary
                player.s_pos[axis] += future_pos - bound_1
                if player.pos[axis] > bound_2: # If in other boundary
                    player.s_pos[axis] += bound_2 - player.pos[axis]
                    for ent in Game.room(0,0).ents:
                        ent.s_pos[axis] -= bound_1 - bound_2
                    Game.room(0,0).layout.s_pos[axis] -= bound_1 - bound_2
                else: # If not in other boundary
                    for ent in Game.room(0,0).ents:
                        ent.s_pos[axis] -= bound_1 - player.pos[axis]
                    Game.room(0,0).layout.s_pos[axis] -= bound_1 - player.pos[axis]
            else: player.s_pos[axis] += player.vel[axis] # if already in boundary
                
        # If will go into right / down boundary
        elif future_pos > bound_2:
            if player.pos[axis] < bound_2: # If not already in boundary
                player.s_pos[axis] += future_pos - bound_2
                if player.pos[axis] < bound_1: # If in other boundary
                    player.s_pos[axis] += bound_1 - player.pos[axis]
                    for ent in Game.room(0,0).ents:
                        ent.s_pos[axis] -= bound_2 - bound_1
                    Game.room(0,0).layout.s_pos[axis] -= bound_2 - bound_1
                else: # If not in other boundary
                    for ent in Game.room(0,0).ents:
                        ent.s_pos[axis] -= bound_2 - player.pos[axis]
                    Game.room(0,0).layout.s_pos[axis] -= bound_2 - player.pos[axis]
            else: player.s_pos[axis] += player.vel[axis] # if already in boundary
                
        # If will go out of either boundary
        elif future_pos >= bound_1 and future_pos <= bound_2:
            if player.pos[axis] <= bound_1: # If going out left / up boundary
                player.s_pos[axis] += bound_1 - player.pos[axis]
                for ent in Game.room(0,0).ents:
                    ent.s_pos[axis] -= future_pos - bound_1
                Game.room(0,0).layout.s_pos[axis] -= future_pos - bound_1
            elif player.pos[axis] >= bound_2: # If going out right / down boundary
                player.s_pos[axis] += bound_2 - player.pos[axis]
                for ent in Game.room(0,0).ents:
                    ent.s_pos[axis] -= future_pos - bound_2
                Game.room(0,0).layout.s_pos[axis] -= future_pos - bound_2
            else: # If already out of boundary
                for ent in Game.room(0,0).ents:
                    ent.s_pos[axis] -= player.vel[axis]
                Game.room(0,0).layout.s_pos[axis] -= player.vel[axis]
        
    def room_check():
        # Checks if player is at edge of room
        
        # Left
        if player.pos[0] == -Game.ROOM_BOUND:
            cam_dist = (Game.room(-1,0).spawn[0][1][1] - Game.room(0,0).spawn[0][0][1]
                      + player.pos[1] - player.s_pos[1])
            Game.room(-1,0).layout.s_pos[0] -= DIMENSIONS[0]
            Game.room(-1,0).layout.s_pos[0] -= Game.room(-1,0).spawn[0][1][0] - DIMENSIONS[0]
            Game.room(-1,0).layout.s_pos[1] -= cam_dist
            for ent in Game.room(-1,0).ents:
                ent.s_pos[0] -= DIMENSIONS[0]
                ent.s_pos[0] -= Game.room(-1,0).spawn[0][1][0] - DIMENSIONS[0]
                ent.s_pos[1] -= cam_dist
                
        # Right
        elif player.pos[0] == Game.room(0,0).bounds[0] + Game.ROOM_BOUND:
            cam_dist = (Game.room(1,0).spawn[0][0][1] - Game.room(0,0).spawn[0][1][1]
                      + player.pos[1] - player.s_pos[1])
            Game.room(1,0).layout.s_pos[0] += DIMENSIONS[0]
            Game.room(1,0).layout.s_pos[1] -= cam_dist
            for ent in Game.room(1,0).ents:
                ent.s_pos[0] += DIMENSIONS[0]
                ent.s_pos[1] -= cam_dist
               
        # Up
        if player.pos[1] == -Game.ROOM_BOUND:
            cam_dist = (Game.room(0,1).spawn[1][1][0] - Game.room(0,0).spawn[1][0][0]
                      + player.pos[0] - player.s_pos[0])
            Game.room(0,1).layout.s_pos[1] -= DIMENSIONS[1]
            Game.room(0,1).layout.s_pos[1] -= Game.room(0,1).spawn[1][1][1] - DIMENSIONS[1]
            Game.room(0,1).layout.s_pos[0] -= cam_dist
            for ent in Game.room(0,1).ents:
                ent.s_pos[1] -= DIMENSIONS[1]
                ent.s_pos[1] -= Game.room(0,1).spawn[1][1][1] - DIMENSIONS[1]
                ent.s_pos[0] -= cam_dist
                                
        # Down
        elif player.pos[1] == Game.room(0,0).bounds[1] + Game.ROOM_BOUND:
            cam_dist = (Game.room(0,-1).spawn[1][0][0] - Game.room(0,0).spawn[1][1][0]
                      + player.pos[0] - player.s_pos[0])
            Game.room(0,-1).layout.s_pos[1] += DIMENSIONS[1]
            Game.room(0,-1).layout.s_pos[0] -= cam_dist
            for ent in Game.room(0,-1).ents:
                ent.s_pos[1] += DIMENSIONS[1]
                ent.s_pos[0] -= cam_dist
                
    def room_trans(canvas):
        # Transition from one room to another
        
        # Left
        if player.pos[0] == -Game.ROOM_BOUND:
            Game.room(-1, 0).layout.draw(canvas)
            for ent in Game.room(-1,0).ents:
                ent.draw(canvas)
                
            # Shift screen
            if round(player.s_pos[0], 0) < DIMENSIONS[0] - Game.ROOM_BOUND:
                Game.room(0, 0).layout.s_pos[0] += Game.ROOM_VEL
                Game.room(-1, 0).layout.s_pos[0] += Game.ROOM_VEL
                for ent in Game.room(0,0).ents:
                    ent.s_pos[0] += Game.ROOM_VEL
                for ent in Game.room(-1,0).ents:
                    ent.s_pos[0] += Game.ROOM_VEL
                player.s_pos[0] += Game.ROOM_VEL
                    
            else: # Change room
                player.pos[0] = Game.room(-1,0).spawn[0][1][0] - Game.ROOM_BOUND
                player.pos[1] = Game.room(-1,0).spawn[0][1][1] - \
                                  Game.room(0,0).spawn[0][0][1] + player.pos[1]
                player.origin[0] = Game.room(-1,0).spawn[0][1][0] - Game.ROOM_SPAWN_BOUND[0]
                player.origin[1] = Game.room(-1,0).spawn[0][1][1]
                player.spawn = 'right'
                Game.reset_room()
                Game.x_pos -= 1
        
        # Right
        elif player.pos[0] == Game.room(0,0).bounds[0] + Game.ROOM_BOUND:
            Game.room(1, 0).layout.draw(canvas)
            for ent in Game.room(1,0).ents:
                ent.draw(canvas)
                
            # Shift screen
            if round(player.s_pos[0], 0) > Game.ROOM_BOUND:
                Game.room(0, 0).layout.s_pos[0] -= Game.ROOM_VEL
                Game.room(1, 0).layout.s_pos[0] -= Game.ROOM_VEL
                for ent in Game.room(0,0).ents:
                    ent.s_pos[0] -= Game.ROOM_VEL
                for ent in Game.room(1,0).ents:
                    ent.s_pos[0] -= Game.ROOM_VEL
                player.s_pos[0] -= Game.ROOM_VEL
                    
            else: # Change room
                player.pos[0] = Game.room(1,0).spawn[0][0][0] + Game.ROOM_BOUND
                player.pos[1] = Game.room(1,0).spawn[0][0][1] - \
                                  Game.room(0,0).spawn[0][1][1] + player.pos[1]
                player.origin[0] = Game.room(1,0).spawn[0][0][0] + Game.ROOM_SPAWN_BOUND[0]
                player.origin[1] = Game.room(1,0).spawn[0][0][1]
                player.spawn = 'left'
                Game.reset_room()
                Game.x_pos += 1
                
        # Up
        elif player.pos[1] == -Game.ROOM_BOUND:
            Game.room(0, 1).layout.draw(canvas)
            for ent in Game.room(0,1).ents:
                ent.draw(canvas)
                
            # Shift screen
            if round(player.s_pos[1], 0) < DIMENSIONS[1] - Game.ROOM_BOUND:
                Game.room(0, 0).layout.s_pos[1] += Game.ROOM_VEL
                Game.room(0, 1).layout.s_pos[1] += Game.ROOM_VEL
                for ent in Game.room(0,0).ents:
                    ent.s_pos[1] += Game.ROOM_VEL
                for ent in Game.room(0,1).ents:
                    ent.s_pos[1] += Game.ROOM_VEL
                player.s_pos[1] += Game.ROOM_VEL
                    
            else: # Change room
                player.pos[1] = Game.room(0,1).spawn[1][1][1] - Game.ROOM_BOUND
                player.pos[0] = Game.room(0,1).spawn[1][1][0] - \
                                  Game.room(0,0).spawn[1][0][0] + player.pos[0]
                player.origin[1] = Game.room(0,1).spawn[1][1][1] - Game.ROOM_SPAWN_BOUND[1]
                player.origin[0] = Game.room(0,1).spawn[1][1][0]
                player.spawn = 'down'
                Game.reset_room()
                Game.y_pos += 1
                
        # Down
        elif player.pos[1] == Game.room(0,0).bounds[1] + Game.ROOM_BOUND:
            Game.room(0,-1).layout.draw(canvas)
            for ent in Game.room(0,-1).ents:
                ent.draw(canvas)
                
            # Shift screen
            if round(player.s_pos[1], 0) > Game.ROOM_BOUND:
                Game.room(0, 0).layout.s_pos[1] -= Game.ROOM_VEL
                Game.room(0, -1).layout.s_pos[1] -= Game.ROOM_VEL
                for ent in Game.room(0,0).ents:
                    ent.s_pos[1] -= Game.ROOM_VEL
                for ent in Game.room(0,-1).ents:
                    ent.s_pos[1] -= Game.ROOM_VEL
                player.s_pos[1] -= Game.ROOM_VEL
                    
            else: # Change room
                player.pos[1] = Game.room(0,-1).spawn[1][0][1] + Game.ROOM_BOUND
                player.pos[0] = Game.room(0,-1).spawn[1][0][0] - \
                                  Game.room(0,0).spawn[1][1][0] + player.pos[0]
                player.origin[1] = Game.room(0,-1).spawn[1][0][1] + Game.ROOM_SPAWN_BOUND[1]
                player.origin[0] = Game.room(0,-1).spawn[1][0][0]
                player.spawn = 'up'
                Game.reset_room()
                Game.y_pos -= 1
                
        else: return True
        
    def respawn():
        if player.spawn == 'left':
            cam_dist = [Game.room(0,0).bounds[0] - DIMENSIONS[0],
                        Game.room(0,0).bounds[1] - DIMENSIONS[1]]
            Game.room(0,0).layout.s_pos[1] -= cam_dist[1]
            for ent in Game.room(0,0).ents:
                ent.s_pos[1] -= cam_dist[1]
            player.s_pos[0] = Game.room(0,0).spawn[0][0][0] + Game.ROOM_SPAWN_BOUND[0]
            player.s_pos[1] = Game.room(0,0).spawn[0][0][1] - cam_dist[1]
            
        if player.spawn == 'right':
            cam_dist = [Game.room(0,0).bounds[0] - DIMENSIONS[0],
                        Game.room(0,0).bounds[1] - DIMENSIONS[1]]
            Game.room(0,0).layout.s_pos[0] -= cam_dist[0]
            Game.room(0,0).layout.s_pos[1] -= cam_dist[1]
            for ent in Game.room(0,0).ents:
                ent.s_pos[0] -= cam_dist[0]
                ent.s_pos[1] -= cam_dist[1]
            player.s_pos[0] = Game.room(0,0).spawn[0][1][0] - Game.ROOM_SPAWN_BOUND[0] - cam_dist[0]
            player.s_pos[1] = Game.room(0,0).spawn[0][1][1] - cam_dist[1]
                
        if player.spawn == 'up':
            cam_dist = [Game.room(0,0).bounds[0] - DIMENSIONS[0],
                        Game.room(0,0).bounds[1] - DIMENSIONS[1]]
            Game.room(0,0).layout.s_pos[0] -= cam_dist[0]
            for ent in Game.room(0,0).ents:
                ent.s_pos[0] -= cam_dist[0]
            player.s_pos[1] = Game.room(0,0).spawn[1][0][1] + Game.ROOM_SPAWN_BOUND[1]
            player.s_pos[0] = Game.room(0,0).spawn[1][0][0] - cam_dist[0]
                
        if player.spawn == 'down':
            cam_dist = [Game.room(0,0).bounds[0] - DIMENSIONS[0],
                        Game.room(0,0).bounds[1] - DIMENSIONS[1]]
            Game.room(0,0).layout.s_pos[0] -= cam_dist[0]
            Game.room(0,0).layout.s_pos[1] -= cam_dist[1]
            for ent in Game.room(0,0).ents:
                ent.s_pos[1] -= cam_dist[1]
                ent.s_pos[0] -= cam_dist[0]
            player.s_pos[1] = Game.room(0,0).spawn[1][1][1] - Game.ROOM_SPAWN_BOUND[1] - cam_dist[1]
            player.s_pos[0] = Game.room(0,0).spawn[1][1][0] - cam_dist[0]

class Room:
    
    def __init__(self,
                 data,
                 obstacles,
                 entities,
                 layout,
                 boundaries,
                 spawn):
        
        self.data = data
        self.obs = obstacles
        self.ents = entities
        self.layout = layout
        self.bounds = boundaries # Room dimensions
        self.spawn = spawn # Spawn locations

class Game:
    
    rooms=[[Room(
            "                                      "
            "                                      "
            "                                      "
            "                                      "
            "                                      "
            "                                      "
            "                                     b"
            "b                                     "
            "b                      s i            "
            "b             i      bbbbb            "
            "b   i   bbbbbbp     pb   b            "
            " bbbbb  b    b   c   b   b            "
            "     b  b    bbbbbbbbb   b     bbbbbbb"
            "     b  b                b     b      "
            "     b  b                b     b      "
            "      hh                  hhhhh       "
            ,[],[],
            Image(Image.ROOM_0, [760, 300],[608, 240]),
            [1520,600], [[[0,405],[1520,445]],[[],[]]])],

           [Room(
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "              s  bb"
            "              bbb  "
            "              b    "
            "             b     "
            "    c   s    b     "
            "bbbbpp  pppbb      "
            "   h         h     "
            "   h         h     "
            "    hhhhhhhhh      "
            ,[],[],
            Image(Image.ROOM_1, [380, 300],[304, 240]),
            [760,600], [[[0,445],[760,245]],[[],[]]])],

           [Room(
            "        bbbbbb    b"
            "                  b"
            "                 pb"
            "                   "
            "       c    s      "
            "    bbbbbb  bbbbbbb"
            "  bb     b  b      "
            "bb       b  b      "
            "         b  b      "
            "         b  b      "
            "         b  b      "
            "         b  b      "
            "         b  b      "
            "         b  b      "
            "         b  b      "
            "          hh       "
            ,[],[],
            Image(Image.ROOM_2, [380, 300],[304, 240]),
            [760,600], [[[0,245],[760,165]],[[700,0],[]]]),
           
            Room(
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            " b                 "
            " b                 "
            " b                 "
            " b                 "
            " b s s             "
            " bbbbb    c        "
            "     b  bbbbbb    b"
            "     b  b    b    b"
            "     b  b    bp   b"
            ,[],[],
            Image(Image.ROOM_2_1, [380, 300],[304, 240]),
            [760,600], [[[],[760,485]],[[],[700,600]]])],
          
           [Room(
            "b                 b"
            "b                 b"
            "b                 b"
            "                   "
            "                   "
            "bb      bbb        "
            " b  bb  bbb  bb    "
            " b  bb       bb  bb"
            "b                b "
            "b                b "
            "b                 b"
            "b                 b"
            "b                 b"
            "b                 b"
            "b                 b"
            " hhhhhhhhhhhhhhhhh "
            ,[],[],
            Image(Image.ROOM_3, [380, 300],[304, 240]),
            [760,600], [[[0,165],[760,245]],[[380,0],[]]]),
           
            Room(
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "         s         "
            "        bbb  s     "
            "    s   bbb  bb    "
            "    bb       bb    "
            "    bb             "
            "bb  bb           bb"
            " b               b "
            " b               b "
            ,[],[],
            Image(Image.ROOM_3_1, [380, 300],[304, 240]),
            [760,600], [[[0,485],[760,485]],[[],[380,600]]])],
          
           [Room(
            "b  b                                  "
            "b                                     "
            "b                                     "
            "                                      "
            "                                      "
            "                                      "
            "                                      "
            "bb                                    "
            " b                                    "
            " b                                    "
            "b                           C         "
            "b           S                         "
            "b                                     "
            "b bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            "b b                                   "
            " h                                    "
            ,[],[],
            Image(Image.ROOM_4, [760, 300],[608, 240]),
            [1520,600], [[[0,245],[]],[[120,0],[]]]),
           
            Room(
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "                   "
            "   b               "
            "   b               "
            "   b               "
            "   b               "
            "   b               "
            "b  b               "
            "b  b               "
            "b  b               "
            ,[],[],
            Image(Image.ROOM_4_1, [380, 300],[304, 240]),
            [760,600], [[[0,485],[]],[[],[120,600]]])]]
    
    # Room coordinates
    x_pos = 0
    y_pos = 0
        
    # Game constants
    WALK_VEL = 0.8
    WALK_ACCEL = 0.2
    WALK_ACCEL_MAX = 3
    WALK_DEACCEL = 0.4
    WALK_DEACCEL_MAX = 0
    DASH_ACCEL = [16, -8]
    DASH_INVIN = 15
    DEACCEL_MAX = 1.2
    JUMP_ACCEL = -12
    KNOCKBACK_ACCEL = 10
    INVIN_TIME = 20
    GRAVITY = 0.8
    GRAVITY_MAX = 40
    DASH_COOLDOWN = 26
    JUMP_COOLDOWN = 14
    MOVE_USAGE = 0
    ATTACK_DURATION = 10
    RESPAWN_COOLDOWN = 100
    DEATH_TIME = 20
    SLIME_JUMP_ACCEL = -14
    SLIME_WALK_VEL = 3
    CRAWLER_WALK_VEL = 1
    ROOM_BOUND = 10
    ROOM_SPAWN_BOUND = [60, 40]
    ROOM_VEL = 20
        
    def start_game():
        global player, background
        player = Character(Weapon(Weapon.RIGHT,[0,0],[42,34],1),
                           Character.IDLE_RIGHT, [60, 405], [20,35], 3)
        background = Image(Image.BACKGROUND, [DIMENSIONS[0]/2,DIMENSIONS[1]/2],[304,240])
        for rooms in Game.rooms:
            for room in rooms:
                for counter, string in enumerate(room.data):
                    if string != ' ':
                        pos = [SCALE/2 + counter % (room.bounds[0]/SCALE) * SCALE,
                               SCALE/2 + counter // (room.bounds[0]/SCALE) * SCALE]
                        thing_dict = {'b': Block(pos),
                                      'h': Hazard(pos),
                                      'p': Platform(pos),
                                      'i': Helper(Helper.LEFT, pos, [16,16], 1),
                                      's': Slime(Slime.DEFAULT, pos, [16,13], 2),
                                      'S': Big_Slime(Big_Slime.DEFAULT, pos, [64, 52], 6),
                                      'c': Crawler(Crawler.LEFT, pos, [24, 17], 3),
                                      'C': Big_Crawler(Big_Crawler.LEFT, pos, [96, 68], 8)}
                        if isinstance(thing_dict[string], Obstacle):
                            room.obs.append(thing_dict[string])
                        elif isinstance(thing_dict[string], Entity):
                            room.ents.append(thing_dict[string])
        player.respawn()
        
    def room(x_change, y_change):
        return Game.rooms[Game.x_pos + x_change][Game.y_pos + y_change]

    def reset_room():
        # Resets room to original layout
        player.hp = player.max_hp
        for ent in Game.room(0,0).ents:
            ent.__init__(ent.image, ent.origin, ent.size, ent.max_hp)
        Game.room(0,0).layout.s_pos = [Game.room(0,0).layout.origin[0],
                                       Game.room(0,0).layout.origin[1]]
# Handler to draw on canvas
def draw(canvas):
    if not player.active: player.respawn()
    background.draw(canvas)
    Game.room(0,0).layout.draw(canvas)
    for ent in Game.room(0,0).ents:
        if ent.on_screen(): ent.draw(canvas)
    player.draw(canvas)
    if not Camera.room_trans(canvas): return
    player.check_velocity()
    for ent in Game.room(0,0).ents:
        if ent.on_screen(): ent.check_velocity()
    for obs in Game.room(0,0).obs:
        if obs.on_screen(): obs.check_collision()
    for ent in Game.room(0,0).ents:
        if ent.on_screen(): ent.check_collision()
    player.check_collision()
    for axis in range(2): Camera.check_collision(player, axis)
    for axis in range(2): Camera.shift(axis)
    for ent in Game.room(0,0).ents:
        if ent.on_screen(): ent.update()
    player.update()
    Camera.room_check()

Game.start_game()

frame=simplegui.create_frame('GAME', DIMENSIONS[0], DIMENSIONS[1])

frame.set_canvas_background('White')

frame.set_keydown_handler(player.key_down)
frame.set_keyup_handler(player.key_up)
frame.set_draw_handler(draw)

frame.start()
