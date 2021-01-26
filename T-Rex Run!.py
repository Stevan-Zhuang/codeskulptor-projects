# A recreation of the google chrome dinosaur game in codeskulptor

import simplegui
import random

FRAME_TITLE = "T-Rex Run!"
FRAME_SIZE = [600, 150]
FRAME_COL = 'White' # Colour of the background

GROUND = 133 # The position of the ground
GRAVITY = 0.7
SCROLL_START_SPEED = 7

SPAWN_FREQUENCY = 45 # How often obstacles appear, a lower number means more

PLAYER_SIZE = [28, 36] # Player hitbox size
PLAYER_STARTPOS = [45, 115]
PLAYER_JUMPVEL = -10.5

CACTUS_DIST = 10 # How far cactus hitbox extends

# Position of UI elements
SCORE_POS = [561.5, 20]
HIGH_SCORE_POS = [495.5, 20]
HIGH_POS = [446.5, 20]
GAME_OVER_POS = [300, 50]
RETRY_POS = [300, 91]

class Image():

    def __init__(self, url, size, frames = 1, frame_time = 1):
        self.image = simplegui.load_image("https://i.imgur.com/" + url + ".png")
        self.size = size
        self.frames = frames
        self.is_animated = self.frames > 1
        self.frame_time = frame_time
        self.frame = 0

    def draw(self, position, canvas):
        canvas.draw_image(self.image,
                          [self.size[0]/2 + self.frame // self.frame_time * self.size[0], self.size[1]/2],
                          self.size,
                          position,
                          self.size)
        self.update()

    def update(self):
        if self.is_animated:
            self.frame += 1
            if self.frame // self.frame_time >= self.frames:
                self.frame = 0

class Font(Image):

    def __init__(self, characters, spacing, url, size, frames = 1, frame_time = 1):
        super(Font, self).__init__(url, size, frames, frame_time)
        self.chars = characters
        self.space = spacing

    def draw(self, text, position, canvas):
        for i in range(len(text)):
            canvas.draw_image(self.image,
                              [self.size[0]/2 + self.frame // self.frame_time * self.size[0],
                               self.size[1]/2 + self.chars.index(text[i]) * self.size[1]],
                              self.size,
                              [position[0] + (-len(text)/2 + i + 0.5) * self.space,
                               position[1]],
                              self.size)
        self.update()

class Object():

    def __init__(self, position, size):
        self.pos = position
        self.size = size

    def draw(self, canvas):
        self.image.draw(self.pos, canvas)
        # Draw object hitbox
        """
        canvas.draw_polygon([[self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2],
                             [self.pos[0] + self.size[0]/2, self.pos[1] - self.size[1]/2],
                             [self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2],
                             [self.pos[0] - self.size[0]/2, self.pos[1] + self.size[1]/2]],
                             1, 'Red')
        """

    def has_collided(self, other_obj):
        return all(abs(self.pos[i] - other_obj.pos[i]) < self.size[i]/2 + other_obj.size[i]/2 for i in range(2))

class Player(Object):

    def __init__(self, position, size):
        super(Player, self).__init__(position, size)
        self.vel = 0
        self.image = game.images['player_running']
        self.is_alive = True
        self.on_ground = True
        self.holding_jump = False
        self.holding_duck = False
        self.is_ducking = False

    def jump(self):
        self.image = game.images['player_idle']
        self.vel = PLAYER_JUMPVEL
        self.on_ground = False

    def duck(self):
        self.image = game.images['player_ducking']
        self.pos[1] += 17/2
        self.size[1] -= 17
        self.is_ducking = True

    def unduck(self):
        self.image = game.images['player_running']
        self.pos[1] -= 17/2
        self.size[1] += 17
        self.is_ducking = False

    def update(self):
        self.vel += (GRAVITY * 6 if self.holding_duck else GRAVITY)
        if self.pos[1] == GROUND - self.size[1]/2:
            self.vel = 0
            if not self.on_ground:
                self.image = game.images['player_running']
                self.on_ground = True
        if self.on_ground and self.holding_duck and not self.is_ducking:
            self.duck()
        if self.is_ducking and not self.holding_duck:
            self.unduck()
        if self.on_ground and self.holding_jump and not self.is_ducking:
            self.jump()
        self.pos[1] += self.vel
        if self.pos[1] + self.size[1]/2 > GROUND:
            self.pos[1] = GROUND - self.size[1]/2
        if not self.is_alive:
            if self.is_ducking:
                self.unduck()
            self.image = game.images['player_dead']

class Cactus(Object):

    def __init__(self, image, position, size):
        super(Cactus, self).__init__(position, size)
        self.image = image

class Game:

    def __init__(self):
        self.high_score = 0
        self.images = {'player_idle':    Image('75jlaYh', [44, 47]),
                       'player_running': Image('HhMk1ly', [44, 47], 2, 5),
                       'player_dead':    Image('4zyCnV3', [44, 47]),
                       'player_ducking': Image('z4owllU', [59, 30], 2, 5),
                       'ground':         Image("Ngd7EZO", [1800, 12]),
                       'sky':            Image('wQTwRdg', [1800, 100]),
                       'smallcactus1':   Image("pXvvyLF", [17, 35]),
                       'smallcactus2':   Image("kwApFXg", [34, 35]),
                       'smallcactus3':   Image("vFwIJHH", [51, 35]),
                       'cactus1':        Image("WvhXau7", [25, 50]),
                       'cactus2':        Image("ZsOJSbZ", [50, 50]),
                       'cactus3':        Image("0hurUWo", [75, 50]),
                       'sans_idle':      Image('k4hjoUX', [54, 64]),
                       'sans_left':      Image('bLjfffT', [40, 64]),
                       'bone1':          Image('Dnckovh', [16, 44]),
                       'bone2':          Image('m1JDfCW', [32, 44]),
                       'bone3':          Image('z6yt8JJ', [48, 44]),
                       'game_over':      Image('ITVQSHm', [191, 11]),
                       'retry':          Image('iC4lyg4', [36, 32])}

        self.font = Font("HI0123456789", 11, 'EGiZ345', [9, 11])
        self.has_started = False

    def start(self):
        self.score = 0
        self.scroll_pos = 0
        self.scroll_speed = SCROLL_START_SPEED

        self.spawn_cooldown = SPAWN_FREQUENCY
        self.next_hundred = 100

        self.player = Player(PLAYER_STARTPOS[:], PLAYER_SIZE[:])
        if not self.has_started:
            self.player.image = self.images['player_idle']

        self.obstacles = []

        self.can_restart = False

    def create_frame(self):
        frame = simplegui.create_frame(FRAME_TITLE,
                                       FRAME_SIZE[0],
                                       FRAME_SIZE[1])
        frame.set_draw_handler(self.draw)
        frame.set_keydown_handler(self.keydown_handler)
        frame.set_keyup_handler(self.keyup_handler)

        frame.start()

    def draw(self, canvas):
        canvas.draw_polygon([[0, 0], [FRAME_SIZE[0], 0], [FRAME_SIZE[0], FRAME_SIZE[1]], [0, FRAME_SIZE[1]]],
                            1, FRAME_COL, FRAME_COL)

        ground = self.images['ground']
        sky = self.images['sky']
        ground.draw([ground.size[0]/2 + self.scroll_pos % (FRAME_SIZE[0] - ground.size[0]), GROUND], canvas)
        sky.draw([sky.size[0]/2 + self.scroll_pos/4 % (FRAME_SIZE[0] - sky.size[0]), 50], canvas)

        for obj in self.obstacles:
            obj.draw(canvas)
        self.player.draw(canvas)

        if 975 < self.score < 1000:
            self.images['sans_idle'].draw([500, 110], canvas)
        if self.score > 1000:
            self.images['sans_left'].draw([500, 110], canvas)

        self.font.draw("{:0>5.0f}".format(self.score), SCORE_POS, canvas)
        self.font.draw("{:0>5.0f}".format(self.high_score), HIGH_SCORE_POS, canvas)
        self.font.draw("HI", HIGH_POS, canvas)

        # Opening animation
        if round(self.player.vel, 2) == 11.2:
            self.has_started = True
        if not self.has_started:
            canvas.draw_polygon([[70, 0], [FRAME_SIZE[0], 0], [FRAME_SIZE[0], FRAME_SIZE[1]], [70, FRAME_SIZE[1]]],
                                 1, FRAME_COL, FRAME_COL)

        if self.player.is_alive:
            self.update()
        else:
            self.images['game_over'].draw(GAME_OVER_POS, canvas)
            self.images['retry'].draw(RETRY_POS, canvas)

    def update(self):
        if self.has_started:
            self.score += self.scroll_speed / 36
            self.scroll_pos -= self.scroll_speed

            if self.score > self.next_hundred:
                self.next_hundred += 100
                self.scroll_speed += 0.3

            if self.spawn_cooldown > 0:
                self.spawn_cooldown -= 1
            if self.spawn_cooldown == 0 and random.randint(0, SPAWN_FREQUENCY) == 0:
                self.spawn_cooldown += SPAWN_FREQUENCY
                number = random.randint(1, 3)
                if self.score < 950:
                    is_small = random.randrange(2)
                    size = [(17 if is_small else 25) * number - CACTUS_DIST, (35 if is_small else 50) - CACTUS_DIST]
                    self.obstacles.append(Cactus(self.images['small' * is_small + 'cactus' + str(number)],
                                                 [FRAME_SIZE[0] + size[0]/2, GROUND - size[1]/2], size))
                if self.score > 1000:
                    size = [16 * number, 44 - 10]
                    self.obstacles.append(Cactus(self.images['bone' + str(number)],
                                                 [FRAME_SIZE[0] + size[0]/2, GROUND - size[1]/2], size))

        for obj in self.obstacles:
            obj.pos[0] -= self.scroll_speed

        for obj in self.obstacles:
            if self.player.has_collided(obj):
                self.player.is_alive = False
                if self.score > self.high_score:
                    self.high_score = self.score

        self.player.update()

    def keydown_handler(self, key):
        if key == simplegui.KEY_MAP['space']:
            self.player.holding_jump = True
            if not self.player.is_alive:
                self.can_restart = True
        if key == simplegui.KEY_MAP['down']:
            self.player.holding_duck = True

    def keyup_handler(self, key):
        if key == simplegui.KEY_MAP['space']:
            self.player.holding_jump = False
            if not self.player.is_alive and self.can_restart:
                self.start()
        if key == simplegui.KEY_MAP['down']:
            self.player.holding_duck = False

game = Game()
game.create_frame()
game.start()
