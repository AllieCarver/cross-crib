"""
Cross-Crib Gui
"""
import os, sys, random
import pygame
from pygame.locals import *

#initialize pygame
pygame.init()

# resource constants
BACKGROUND_WIDTH = 900
BACKGROUND_HEIGHT = 728
CARD_WIDTH = 84
CARD_HEIGHT = 122
GRID_OFFSETX = 24
GRID_OFFSETY = 26
GRID_SPACINGX = 100
GRID_SPACINGY = 138
GRID_SIZE = 682
GRID_DIM = 5
# player contants
HUMAN =  1
COMPUTER = 2

def load_image(name, colorkey=None, alpha=False):
    """
    image load function, exits if resources fail to load
    """
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

class CrossCribGUI:
    """
    main GUI class
    """

    def __init__(self, board):
        self._board = board       
        self._screen =  pygame.display.set_mode((BACKGROUND_WIDTH,
                                                 BACKGROUND_HEIGHT))
        self._screen_rect = self._screen.get_rect()
        pygame.display.set_caption('CrossCrib')
        self._background, dummy_rect = load_image('bg.png', True)
        self._loadscreen, dummy_rect = load_image('loadscreen.png', True)
        self._turn = HUMAN
        self._deck = Deck()
        self._grid = Grid()
        self._grid.rect.x = GRID_OFFSETX
        self._grid.rect.y = GRID_OFFSETY
        
        ###
        self.tempcards = self._deck._cards.keys()
        self._currentcard = self.tempcards.pop()
        ###
        self.main()
        
            
    def keydown(self, event):
        """
        keydown handler
        """
        
        key = event.key

        if key == K_ESCAPE:
            sys.exit()

    def click(self, event):
        """
        click handler
        """
        
        pos = event.pos
        for space in self._grid.sprites():
            if space.rect.collidepoint(pos):
                print 'collide'
                if space._card == None:
                    space._card = self._currentcard
                    ###
                    self._currentcard = self.tempcards.pop()

    def update(self):
        """
        updablit current boardu
        """
        for space in self._grid.sprites():
            if space._card:
                card = space._card        
                self._screen.blit(self._deck._cards[card].image, space.rect)
    
    def main(self):
        """
        main game loop
        """
        
        clock = pygame.time.Clock()
        while 1:
            clock.tick(60)
            self._screen.blit(self._background, self._screen_rect)
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.keydown(event)
                elif event.type == MOUSEBUTTONDOWN:
                    self.click(event)

            self._grid.draw(self._grid.image)
            self._screen.blit(self._grid.image, self._grid.rect)
            self.update()
            pygame.display.flip()
            
class Grid(pygame.sprite.Group):
    """
    board grid
    """

    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self.rect.x = GRID_OFFSETX
        self.rect.y = GRID_OFFSETY
        self.make_grid()
        
    def make_grid(self):
        """
        make grid of game space sprites for click collisions
        """
        for row in xrange(GRID_DIM):
            for col in xrange(GRID_DIM):
                space = Space(row, col)
                space.rect.x = GRID_SPACINGX * col + GRID_OFFSETX
                space.rect.y = GRID_SPACINGY * row + GRID_OFFSETY
                self.add(space)
                
class Space(pygame.sprite.Sprite):
    """
    grid space
    """

    def __init__(self, row, col):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()
        self._card = None
        self.row = row
        self.col = col

    def set_card(self, card):
        self._card =  card

    def get_card(self):
        return self._card
    
class Deck(pygame.sprite.Group):
    """
    Deck of cards
    """

    def __init__(self):
        #call Group constructor
       pygame.sprite.Group.__init__(self)
       

    def __init__(self):
        #call Group constructor
        pygame.sprite.Group.__init__(self)
        self._suits = ['spade', 'club', 'diamond', 'heart']
        self._cards_per_suit = 13
        self._cards = {}
        self._cards_sprite, dummy_rect = load_image('cards.png',alpha = True)
        self.make_cards()

    def __str__(self):
        string = """
                 {0}

                 {1}
                 """.format(self.sprites(), self._cards)
        return string
        
    def make_cards(self):
        """
        slice sprite-sheet construct individual card sprites
        """

        for suit in self._suits:
            for card_num in xrange(1, self._cards_per_suit + 1):
                image = self._cards_sprite.subsurface((
                    CARD_WIDTH * (card_num - 1),
                    CARD_HEIGHT * self._suits.index(suit),
                    CARD_WIDTH, CARD_HEIGHT))
                rect = image.get_rect()
                card = Card(card_num, suit, image, rect)
                self._cards[str(card)] = card
                self.add(card)
        #card back last row, col = 4,1
        image = self._cards_sprite.subsurface((
                    CARD_WIDTH,
                    CARD_HEIGHT * 4,
                    CARD_WIDTH, CARD_HEIGHT))
        rect = image.get_rect()
        card = Card(14, 'cardback', image, rect)
        self._cards[str(card)] = card 
        #card back
        
class Card(pygame.sprite.Sprite):
    """
    Class to represent playing card sprite
    """

    def __init__(self, card, suit, image, rect):
        #call Sprite constuctor
        pygame.sprite.Sprite.__init__(self)
        #set card image
        self.image = image
        self.rect = rect
        self.suit = suit
        self._card = str(card)+suit
        if card > 10:
            self.value = 10
        else:
            self.value = card 

    def __str__(self):
        return str(self._card) + self.suit 
    

gui = CrossCribGUI(None)
