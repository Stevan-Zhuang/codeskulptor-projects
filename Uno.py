# Uno the card game
# By Stevan Zhuang

import simplegui, random, math

LENGTH = 700
COLOURS = ['red','blue','green','yellow',
           'black']
SYMBOLS = ['0','1','2','3','4','5','6','7','8','9','reverse','stop','draw2',
           'wild','draw4',
           'wildplayed','draw4played']
CARD_SIZE = (66, 102)
CARD_IMAGE = simplegui.load_image('https://i.imgur.com/grWoVXD.png')
CARD_BACKGROUND = simplegui.load_image('https://i.imgur.com/4CJUMyq.png')
CARD_BACK = simplegui.load_image('https://i.imgur.com/IkjAw92.png')

class Button:
    # Parent class for clickable objects
    def __init__(self, image, position, size):
        self.image = image
        self.pos = position
        self.size = size
   
    def clicked(self, pos):
        return (abs(pos[0] - self.pos[0]) <= self.size[0]/2 and
                abs(pos[1] - self.pos[1]) <= self.size[1]/2)
   
    def draw(self, canvas, tile):
        canvas.draw_image(self.image,
                          tile,
                          self.size,
                          self.pos,
                          self.size)

class Card(Button):
   
    def __init__(self, colour, symbol):
        self.colour = colour
        self.symbol = symbol
        self.size = CARD_SIZE

    def reset(self):
        # Changes wild cards back to their original form
        if self.symbol[-6:] == 'played':
            self.colour = 'black'
            self.symbol.replace('played', '')
       
    def draw(self, canvas):
        background_tile = (self.size[0]/2 + self.size[0]*COLOURS.index(self.colour),
                           self.size[1]/2)
        image_tile = (self.size[0]/2 + self.size[0]*SYMBOLS.index(self.symbol),
                      self.size[1]/2)
        canvas.draw_image(CARD_BACKGROUND,
                          background_tile,
                          self.size,
                          self.pos,
                          self.size)
        canvas.draw_image(CARD_IMAGE,
                          image_tile,
                          self.size,
                          self.pos,
                          self.size)

    def draw_flipped(self, canvas, angle):
        canvas.draw_image(CARD_BACK,
                         (self.size[0]/2,
                          self.size[1]/2),
                          self.size,
                          self.pos,
                          self.size,
                          angle)

class Hand:
   
    def __init__(self):
        self.cards = []

    def draw_card(self, num):
        for i in range(num):
            self.cards.append(game.deck.deal_card())
        self.set_card_pos()
       
    def can_play(self, card):
        # Wild can be played at any time
        if card.symbol == 'wild': return True
        # Draw 4 can only be played when other cards can
        elif card.symbol == 'draw4':
            return not any(card.symbol != 'draw4' and self.can_play(card)
                   for card in self.cards)
        return (card.colour == game.pile.cards[-1].colour or
                card.symbol == game.pile.cards[-1].symbol)

class User(Hand):

    def check_cards(self, pos):
        for card in self.cards[::-1]:
            if card.clicked(pos):
                if self.can_play(card):
                    game.play(card)
                    # You can only play one card at once
                    break

    def choose_colour(self):
        game.buttons.append(game.choose_red)
        game.buttons.append(game.choose_blue)
        game.buttons.append(game.choose_green)
        game.buttons.append(game.choose_yellow)
                   
    def set_card_pos(self):
        for card in self.cards:
            pos = self.cards.index(card) + 0.5 -len(self.cards)/2.0
            dist = (LENGTH - CARD_SIZE[0] - CARD_SIZE[1]*4)/len(self.cards)
            # Cards have a max distance apart
            if dist > CARD_SIZE[0]: dist = CARD_SIZE[0]
            card.pos = [LENGTH/2 + pos*dist,
                        LENGTH - CARD_SIZE[1]]
           
    def draw(self, canvas):
        for card in self.cards:
            card.draw(canvas)

class Bot(Hand):
   
    def check_cards(self):
        if any(self.can_play(card) for card in self.cards):
            for card in self.cards:
                if self.can_play(card):
                    game.play(card)
                    # Stops bot from playing multiple cards
                    break
        else: game.pass_turn()
           
    def choose_colour(self):
        # Chooses the colour with the most amount in hand
        colours = {'red': 0, 'blue': 0, 'green': 0, 'yellow': 0}
        for card in self.cards:
            if card.colour in colours:
                colours[card.colour] += 1
        colour = None
        max_val = -1
        for col in colours.keys():
            if colours[col] > max_val:
                max_val = colours[col]
                colour = col
        game.held.colour = colour
        game.play_card()
           
    def set_card_pos(self):
        for card in self.cards:
            pos = self.cards.index(card) + 0.5 -len(self.cards)/2.0
            dist = (LENGTH - CARD_SIZE[0] - CARD_SIZE[1]*4)/len(self.cards)
            # Cards have a max distance apart
            if dist > CARD_SIZE[0]: dist = CARD_SIZE[0]
            turn = game.hands.index(self)
            if turn == 1: card.pos = [CARD_SIZE[1], LENGTH/2 + pos*dist]
            elif turn == 2: card.pos = [LENGTH/2 + pos*dist, CARD_SIZE[1]]
            elif turn == 3: card.pos = [LENGTH - CARD_SIZE[1], LENGTH/2 + pos*dist]
       
    def draw(self, canvas):
        angle = game.hands.index(self)*90*math.pi/180
        for card in self.cards:
            card.draw_flipped(canvas, angle),

class Deck(Button):
   
    def __init__(self):
        self.cards = []
        for colour in COLOURS[:4]:
            for symbol in SYMBOLS[1:13]:
                self.add_card(colour, symbol, 2)
            self.add_card(colour, '0', 1)
        for symbol in SYMBOLS[13:15]:
            self.add_card('black', symbol, 2)
        Button.__init__(self, CARD_BACK,
                       (LENGTH/2 - CARD_SIZE[0]/1.5, LENGTH/2),
                        CARD_SIZE)
               
    def add_card(self, colour, symbol, num):
        for i in range(num):
            self.cards.append(Card(colour, symbol))

    def shuffle(self):
        random.shuffle(self.cards)
        # Top card cannot be draw 4
        while self.cards[0].symbol == 'draw4':
            self.shuffle()
       
    def deal_card(self):
        return self.cards.pop(0)
        # Resets if there are no more cards
        if len(self.cards) == 0:
            game.set_game()
   
    def mouse_click(self, pos):
        if self.clicked(pos):
            game.pass_turn()

class Pile:
   
    def __init__(self):
        self.cards = []
       
    def add(self, card):
        self.cards.append(card)
        self.set_card_pos()
       
    def deal_card(self):
        self.cards[0].reset()
        return self.cards.pop(0)
   
    def reset(self):
        for card in self.cards:
            game.deck.cards.append(self.deal_card())

    def set_card_pos(self):
        top = self.cards[-3:]
        for card in top:
            pos = top.index(card) + 0.5 -len(top)/2.0
            card.pos = [LENGTH/2 + CARD_SIZE[0]/1.5 + pos*10,
                        LENGTH/2]

    def draw(self, canvas):
        for card in self.cards[-3:]:
            card.draw(canvas)

class Choose_Colour(Button):
    # Chooses colour for wild card
    def __init__(self, position, colour):
        self.colour = colour
        Button.__init__(self, CARD_BACKGROUND,
                        position, CARD_SIZE)
       
    def mouse_click(self, pos):
        if self.clicked(pos):
            game.held.colour = self.colour
            game.buttons = []
            game.play_card()

class Game:
   
    choose_red = Choose_Colour((LENGTH/2-115,LENGTH/2-115), 'red')
    choose_blue = Choose_Colour((LENGTH/2+115,LENGTH/2-115), 'blue')
    choose_green = Choose_Colour((LENGTH/2+115,LENGTH/2+115), 'green')
    choose_yellow = Choose_Colour((LENGTH/2-115,LENGTH/2+115), 'yellow')

    def __init__(self):
        self.hands = [User(), Bot(), Bot(), Bot()]
        self.deck = Deck()
        self.set_effects()
        self.deck.shuffle()
        self.pile = Pile()
        self.turn = random.choice(self.hands)
        self.change = 1 # The direction of the next player
        self.buttons = [] # Choose colour buttons

    def start(self):
        # Creates new game
        self.in_play = True
        self.winner = None
        for hand in self.hands:
            hand.cards = []
            hand.draw_card(7)
        self.set_game()
        self.check_turn()
       
    def set_game(self):
        # Puts pile back in deck
        self.pile.reset()
        self.deck.shuffle()
        self.play(self.deck.deal_card())
       
    def new_game(self):
        self.in_play = False
        new_game_timer.start()
       
    def new_game_timer(self):
        new_game_timer.stop()
        self.__init__()
        self.start()
   
    def set_effects(self):
        # Gives cards in the deck their effects
        effect_dict = {'reverse': lambda: self.switch_path(),
                       'stop': lambda: self.switch_turn(),
                       'draw2': lambda: [self.next_turn().draw_card(2),
                                         self.switch_turn()],
                       'draw4': lambda: [self.next_turn().draw_card(4),
                                         self.switch_turn()]}
        for card in self.deck.cards:
            card.play = effect_dict.get(card.symbol, lambda: None)
           
    def play_card(self):
        if self.held.symbol == 'wild' or self.held.symbol == 'draw4':
            self.held.symbol += 'played'
        self.pile.add(self.held)
        if self.held in self.turn.cards:
            self.turn.cards.remove(self.held)
        self.turn.set_card_pos()
        if len(self.turn.cards) == 0:
            self.in_play = False
            self.winner = self.turn
        self.held.play()
        self.end_turn()
       
    def play(self, card):
        self.held = card
        if self.held.colour == 'black':
            self.turn.choose_colour()
        else: self.play_card()
         
    # Plays a card with delay
    def will_play(self, card):
        self.held = card
        if self.held.colour == 'black':
            self.turn.choose_colour()
        else: play_timer.start()
           
    def pass_turn(self):
        self.turn.draw_card(1)
        card = self.turn.cards[-1]
        if self.turn.can_play(card):
            self.will_play(card)
        else: self.end_turn()
           
    def play_timer(self):
        # Passing and drawing a playable card has a delay
        play_timer.stop()
        self.play(self.held)
       
    def bot_timer(self):
        # Bot has delay before playing
        bot_timer.stop()
        self.turn.check_cards()

    # Handler for mouse click
    def mouse_click(self, pos):
        # Select colour
        if self.buttons:
            for button in self.buttons:
                button.mouse_click(pos)
        elif self.in_play and isinstance(self.turn, User) and not play_timer.is_running():
            self.turn.check_cards(pos)
            self.deck.mouse_click(pos)
           
    def end_turn(self):
        self.switch_turn()
        self.check_turn()

    def check_turn(self):
        if self.in_play and isinstance(self.turn, Bot):
            bot_timer.start()

    def switch_turn(self):
        if self.in_play: self.turn = self.next_turn()
       
    def next_turn(self):
        # Returns the next player to move
        index = self.hands.index(self.turn)
        return self.hands[(index + self.change)%len(self.hands)]
   
    def switch_path(self):
        # Switches next player from right to left and vice versa
        self.change *= -1

    # Handler to draw on canvas
    def draw(self, canvas):
        canvas.draw_image(simplegui.load_image('https://i.imgur.com/e83qzdU.png'),
                         (350,350),
                         (700,700),
                         (LENGTH/2, LENGTH/2),
                         (700,700))
        for hand in self.hands:
            hand.draw(canvas)
        deck_tile = (CARD_SIZE[0]/2, CARD_SIZE[1]/2)
        self.deck.draw(canvas, deck_tile)
        self.pile.draw(canvas)
        for button in self.buttons:
            tile = (button.size[0]/2 + button.size[0]*COLOURS.index(button.colour),
                    button.size[1]/2)
            button.draw(canvas, tile)
        if not self.in_play and self.winner:
            if isinstance(self.winner, User):
                canvas.draw_text('YOU WON', (175, 250), 75, 'black')
            else: canvas.draw_text('YOU LOST', (175, 250), 75, 'black')

game = Game()

# Create a frame and assign callbacks to event handlers
frame = simplegui.create_frame("UNO", LENGTH, LENGTH)

frame.add_button('New Game', game.new_game)

# Game rules
frame.add_label('How To Play:')
frame.add_label('- Play a card that matches the colour or symbol of the top of the pile')
frame.add_label('- Click a card in your hand to play it')
frame.add_label('- Click on the deck to draw a card and pass your turn')
frame.add_label('- When the drawn card can be played, it must be played')
frame.add_label('- There are actions cards with special effects')
frame.add_label('- Skip: Skips the next players turn')
frame.add_label('- Reverse: Changes the direction of players')
frame.add_label('- Draw 2: The next player draws 2 cards and skips their turn')
frame.add_label('- Wild: This cards colour becomes the choice of the user')
frame.add_label('- Wild Draw 4: Wild effect and the next player draws 4 cards and skips their turn')
frame.add_label('- A Wild Draw 4 can only be played when the user has no other playable cards')

frame.set_mouseclick_handler(game.mouse_click)

new_game_timer = simplegui.create_timer(1000, game.new_game_timer)
play_timer = simplegui.create_timer(500, game.play_timer)
bot_timer = simplegui.create_timer(500, game.bot_timer)

frame.set_draw_handler(game.draw)

# Start the game
game.start()

# Start the frame animation
frame.start()
