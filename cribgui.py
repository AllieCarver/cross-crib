#!/usr/bin/env python
"""
Cross-Crib Gui
"""
import os, sys, random
import pygame
from pygame.locals import *
import json
import crosscrib

#initialize pygame
pygame.init()

# resource constants
WIDTH = 900
HEIGHT = 728
CARD_WIDTH = 84
CARD_HEIGHT = 122
GRID_OFFSETX = 24
GRID_OFFSETY = 26
GRID_SPACINGX = 100
GRID_SPACINGY = 138
GRID_SIZE = 682
GRID_DIM = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_image(name, colorkey=None, alpha=False):
    """
    image load function, exits if resources fail to load
    """
    name = os.path.join('data', name)
    #fullname = resource_path(fullname)
    #fullname = resource_path(name)
    #with open('/home/killerdigby/python-game-project/output.txt', 'w') as tfile:
    #    tfile.write(fullname)
        
    try:
        image = pygame.image.load(name)
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

    def __init__(self):
        #intialize pygame screen and setup 
        self._setup_screens()
        #init fonts
        self._setup_fonts()
        #setup game menus
        self._setup_menus()
        self._setup_options()
        self._crib_pos = {'human':440, 'computer': 170}
        self._turn = ''
        self._continued = False
        self._scored = False
        self.hand_info = None
        self._deck = Deck()
        self._game = crosscrib.CrossCrib(self._deck)  
        self._grid = Grid()
        self._grid.rect.x = GRID_OFFSETX
        self._grid.rect.y = GRID_OFFSETY
        
        #enter main loop
        self.main()
    
        
    def _setup_fonts(self):
        pygame.font.init()
        font = os.path.join('data', 'AlfaSlabOne-Regular.ttf')
        self._font = pygame.font.Font(font, 15)
        self._bigfont = pygame.font.Font(font, 25)
        self._smallfont = pygame.font.Font(font, 10)
        
    def _setup_screens(self):
        pygame.display.set_caption('CrossCrib', 'CrossCrib')
        self._screen =  pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        self._screen_rect = self._screen.get_rect()
        self._background, dummy_rect = load_image('bg.png', True)
        self._loadscreen, dummy_rect = load_image('loadscreen.png', True)
        self._scorebg = pygame.Surface((WIDTH - 100, HEIGHT - 100))
        self._scorebg.set_alpha(230)
        self._scorebg.fill(BLACK)
        self._continue_button = pygame.Surface((200, 50))
        self._continue_button.set_alpha(0)
        self._continue_rect =  self._continue_button.get_rect(left=550,top=610)
        self._deal_btn =  pygame.Surface((200, 50))
        self._deal_btn.set_alpha(0)
        self._deal_rect = self._deal_btn.get_rect(left=550, top=340)
        self._scorenumbg = pygame.Surface((38, 38))
        self._scorenumbg.fill(WHITE)
        self._discard, self._discard_rect = load_image('discard.png', alpha=True)
        self._discard_pos =  3000, 3000
        
    def _setup_menus(self):
        """
        initialize menu button surfaces and rects, text etc
        """
        self._menu_open = False
        self._menu = pygame.Surface((136, 150))
        self._menu_rect = self._menu.get_rect(left=750, top=25)
        self._menubtn = pygame.Surface((150,15))
        self._menubtn.set_alpha(0)
        self._menubtn_rect = self._menubtn.get_rect(left=850, top=12)
        btn = pygame.Surface((136,50))
        btn.set_alpha(90)
        btn.fill(WHITE)
        self._mnewgame = btn.copy()
        self._mnewgame_rect = self._mnewgame.get_rect(left=750, top=25)
        self._mngtext = self._font.render('Newgame', True, BLACK)
        self._mngtext_rect = self._mngtext.get_rect(
                            centerx=self._mnewgame_rect.centerx,
                            centery=self._mnewgame_rect.centery)
        padding = self._mngtext_rect.x - self._mnewgame_rect.x 
        self._opt_menu = pygame.Surface((136, 150))
        self._opt_menu_open = False
        self._opt_menu_rect = self._opt_menu.get_rect(left=615, top=75)
        self._opt_autodeal = btn.copy()
        self._autodeal_rect = self._opt_autodeal.get_rect(left=615, top=75)
        self._autodealtext = self._font.render('Autodeal', True, BLACK)
        self._autodealtext_rect = self._autodealtext.get_rect(
                                    x=self._autodeal_rect.x + padding,
                                    centery=self._autodeal_rect.centery)
        self._opt_autocut = btn.copy()
        self._autocut_rect = self._opt_autocut.get_rect(left=615, top=125)
        self._autocuttext = self._font.render('Autocut', True, BLACK)
        self._autocuttext_rect = self._autocuttext.get_rect(
                                   x=self._autocut_rect.x + padding,
                                   centery=self._autocut_rect.centery)
        self._opt_soundonoff = btn.copy()
        self._soundonoff_rect = self._opt_soundonoff.get_rect(left=615, top=175)
        self._soundtext = self._font.render('Mute', True, BLACK)
        self._soundtext_rect = self._soundtext.get_rect(
                                 x=self._soundonoff_rect.x + padding,
                                 centery=self._soundonoff_rect.centery)
        self._moptions = btn.copy()
        self._moptions_rect = self._moptions.get_rect(left=750, top=75)
        self._moptext = self._font.render('Options', True, BLACK)
        self._moptext_rect = self._moptext.get_rect(
                             x=self._mngtext_rect.x,
                             centery=self._moptions_rect.centery)
        self._mquit = btn.copy()
        self._mquit_rect = self._mquit.get_rect(left=750, top=125)
        self._mqtext = self._font.render('Quit', True, BLACK)
        self._mqtext_rect = self._mqtext.get_rect(
                            x=self._mngtext_rect.x,
                            centery=self._mquit_rect.centery)
        menu_text = self._smallfont.render('Menu', True, BLACK)
        self._background.blit(menu_text, (850,12))

    def _setup_options(self):
        filename = os.path.join('data', 'options.json')
        try:
            with open(filename, 'r') as f:
                self.options = json.load(f)
        except Exception as e:
            print e
            self.options = {'autodeal':False, 'autocut':False, 'mute':False}

    def _save_options(self):
        filename = os.path.join('data', 'options.json')
        try:
            with open(filename, 'w') as f:
                json.dump(self.options, f)
        except:
            pass

        
    def keydown(self, event):
        """
        keydown handler
        """
        
        key = event.key

        if key == K_ESCAPE:
            sys.exit()

        elif key == K_c:
            self.continue_game()
        elif key == K_d:
            self._game.deal()
            self._grid.clear()
            if self._game._dealer == 'computer':
                self._turn = 'human'
                self._game._cut = True
            else:
                self._turn  = 'computer'
                pygame.time.wait(500)
                
        elif key == K_n:
            self.newgame()

        elif key == K_a:
            if self._game._dealer:
                self._continued = False
                self._scored = False
                self.newgame()
                self.autofill()
            else:
                self.autofill()

    def autofill(self):
        self.cut_for_deal()
        if self._game._dealer == 'human':
            self._game.deal()
            self._game._cut = True
        while not self._grid.is_full():
            if self._turn == 'human':
                spaces =  [space for space in self._grid.sprites()
                           if space._card is None]
                if self._grid.centrespace  in spaces:
                    spaces.remove(self._grid.centrespace)
                move = spaces.pop()
                row, col = move.row, move.col
                card = self._game._human_player.card
                self._game._board[row][col] = card
                self._grid.spaces[(row,col)]._card = card
                self._game._human_player.next_card()
                self._turn = 'computer'
            else:
                self.move_ai()
                self._turn = 'human'
                
    def menu_open(self):
        collide = True
        collide2 = False
        collide3 = False
        self._menu_open = True
        while (collide or collide2 or collide3) and self._menu_open:
            self.update()
            pos = pygame.mouse.get_pos()
            collide =  self._menubtn_rect.collidepoint(pos)
            collide2 = self._menu_rect.collidepoint(pos)
            collide3 = False
            #self._screen.blit(self._menu, self._menu_rect)
            self._screen.blit(self._background, self._menu_rect,
                             area=self._menu_rect)
            if self._mnewgame_rect.collidepoint(pos):
                self._screen.blit(self._mnewgame, self._mnewgame_rect)
                #pygame.draw.rect(self._screen, (0,0,0,1), self._mnewgame_rect)
            elif (self._moptions_rect.collidepoint(pos) or
                self._opt_menu_rect.collidepoint(pos)):
                collide3 = self._opt_menu_rect.collidepoint(pos)
                if collide3:
                    self._opt_menu_open = True
                else:
                    self._opt_menu_open = False
                self._screen.blit(self._moptions, self._moptions_rect)
                self._screen.blit(self._background,
                                  self._opt_menu_rect,
                                  area=self._opt_menu_rect)                
                if self._autodeal_rect.collidepoint(pos):
                    self._screen.blit(self._opt_autodeal, self._autodeal_rect)
                elif self._autocut_rect.collidepoint(pos):
                    self._screen.blit(self._opt_autocut, self._autocut_rect)
                elif self._soundonoff_rect.collidepoint(pos):
                    self._screen.blit(self._opt_soundonoff,
                                      self._soundonoff_rect)
                self._screen.blit(self._autodealtext, self._autodealtext_rect)
                self._screen.blit(self._autocuttext, self._autocuttext_rect)
                self._screen.blit(self._soundtext, self._soundtext_rect)
                pygame.draw.rect(self._screen, BLACK, self._opt_menu_rect, 1)
                x = self._autodeal_rect.x + 116
                y = self._autodeal_rect.centery - 5
                pygame.draw.rect(self._screen, BLACK, (x,y, 10, 10), 1)
                if self.options['autodeal']:
                    rect = (x + 1, y + 1, 8, 8)
                    pygame.draw.rect(self._screen, (58, 229, 52), rect)
                y = self._autocut_rect.centery - 5
                pygame.draw.rect(self._screen, BLACK, (x,y, 10, 10), 1)
                if self.options['autocut']:
                    rect = (x + 1, y + 1, 8, 8)
                    pygame.draw.rect(self._screen, (58, 229, 52), rect)
                y = self._soundonoff_rect.centery - 5
                pygame.draw.rect(self._screen, BLACK, (x,y, 10, 10), 1)
                if self.options['mute']:
                    rect = (x + 1, y + 1, 8, 8)
                    pygame.draw.rect(self._screen, (58, 229, 52), rect)                    
                                     
            
            elif self._mquit_rect.collidepoint(pos):
                self._screen.blit(self._mquit, self._mquit_rect)
            pygame.draw.rect(self._screen, BLACK, self._menu_rect, 1)
            self._screen.blit(self._mqtext, self._mqtext_rect)
            self._screen.blit(self._moptext, self._moptext_rect)
            self._screen.blit(self._mngtext, self._mngtext_rect)
            pygame.display.flip()
            self.process_events()
        self._menu_open = False
                
    def click(self, event):
        """
        click handler
        """
        #get position coordinates of event
        pos = event.pos
        #check menu click
        #if self._menubtn_rect.collidepoint(pos):
        #    self.menu_open()
        if self._menu_open:
            if self._mnewgame_rect.collidepoint(pos):
                self._menu_open = False
                self.newgame()
            elif self._mquit_rect.collidepoint(pos):
                self.quit()
            elif self._opt_menu_open:
                if self._autodeal_rect.collidepoint(pos):
                    self.toggle_option('autodeal')
                elif self._autocut_rect.collidepoint(pos):
                    self.toggle_option('autocut')
                elif self._soundonoff_rect.collidepoint(pos):
                    self.toggle_option('mute')
                    
        #only check these conditionals if human turn and game already cut
        if self._turn == 'human' and self._game._cut:
            #iterate spaces of the game grid
            for space in self._grid.sprites():
                #check collision ommit centre space(cut card)
                if (space.rect.collidepoint(pos) and
                    space is not self._grid.centrespace):
                    #set clicked gui space to human card if empty
                    if space._card == None:
                        space._card = self._game._human_player.card
                        row = space.row
                        col = space.col
                        #update game board for use by score funtions
                        self._game._board[row][col] = space._card
                        #get player's next card
                        self._game._human_player.next_card()
                        #switch turns
                        self._turn = 'computer'
            #check for crib discard click
            if (self._discard_rect.collidepoint(pos) and (not
                self._game._human_player.discarded)):
                #discard human player card to crib
                self._game.crib_discard(self._game._human_player)
                #blit next human card so current card shows
                card = self._game._human_player.card
                self._screen.blit(card.image, self._discard_rect)
                        
        if (self._game._dealer == None and not self._game._inprogress and
                self._grid.centrespace.rect.collidepoint(pos)):
            self.cut_for_deal()

        if self._game._dealer == 'human':
            if (self._game._inprogress == True and not self._game._cut):
                if self._grid.centrespace.rect.collidepoint(pos):
                    self._game._cut = True
                    row = self._grid.centrespace.row
                    col = self._grid.centrespace.col
                    self._game._board[row][col] = self._game._cutcard
            else:
                if self._deal_rect.collidepoint(pos):
                    self.deal()
            
            
        if self._scored:
            if self._continue_rect.collidepoint(pos):
                if not self._game._gameover:
                    self.continue_game()
                else:
                    self.newgame()
            

    def autosave(self):
        pass

    def toggle_option(self, option):
        self.options[option] = not self.options[option]

    def quit(self):
        """
        save current game and exit
        """
        self.autosave()
        self._save_options()
        sys.exit()
        
    def cut_for_deal(self):        
        
        comp, human = self._game.cut_for_deal()
        if comp.cardnum == human.cardnum:
            return self.cut_for_deal()
        elif comp.cardnum > human.cardnum:
            self._game._dealer = 'computer'
            self._turn = 'human'
            pygame.time.wait(500)
            self._game.deal()
            self._game._cut = True
            self._grid.clear()
        else:
            self._game._dealer = 'human'
            self._turn = 'computer'
        self._screen.blit(comp.image, (760,25))
        self._screen.blit(human.image, (760, 580))
        self.draw_scoreboard()
        pygame.display.flip()
        pygame.time.wait(2000)


    def deal(self):
        self._game.deal()
        self._grid.clear()
        if self._game._dealer == 'computer':
            self._turn = 'human'
            self._game._cut = True
        else:
            self._turn  = 'computer'
            pygame.time.wait(500)
        
    def newgame(self):
        
        self._game.reset()
        self._grid.clear()
        self._scored = False

    def draw_hands(self):
        """
        draws player and comp held cards
        """
        offset = 10
        cardsinhand = len(self._game._comp_player.hand)
        for idx in xrange(cardsinhand):
            self._screen.blit(self._deck._cardback.image,
                              (650 + offset * idx, 25))
        card = self._game._comp_player.card
        if card:
            self._screen.blit(card.image, (650 + offset * (cardsinhand), 25))

        cardsinhand = len(self._game._human_player.hand)
        for idx in xrange(cardsinhand):
            self._screen.blit(self._deck._cardback.image,
                              (650 + offset * idx, 580))
        card = self._game._human_player.card
        if card:
            self._screen.blit(card.image, (650 +offset * (cardsinhand), 580))
        self._discard_pos = 650 + offset * (cardsinhand), 580
        

    def check_hover(self):
        #move discard rect so it is over up-turned card in hand
        self._discard_rect.topleft = self._discard_pos
        #check collision
        collision = self._discard_rect.collidepoint(pygame.mouse.get_pos())
        #while collions and not yet discarded run loop to draw discard overlay
        while collision and (not self._game._human_player.discarded):         
            if self._game._cut:
                card = self._game._human_player.card.image
                self._screen.blit(card, self._discard_pos)
                self._screen.blit(self._discard, self._discard_pos)
            pygame.display.update(self._discard_rect)
            collision = self._discard_rect.collidepoint(pygame.mouse.get_pos())
            self.process_events()
            pygame.event.pump()
            

    def process_events(self):
        for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN:
                    self.keydown(event)
                elif event.type == MOUSEBUTTONDOWN:
                    self.click(event)
                elif event.type == MOUSEMOTION:
                    pos = event.pos
                    if self._menubtn_rect.collidepoint(pygame.mouse.get_pos()):
                        self.menu_open()

    def move_ai(self):
        moves = self._game.move_ai()
        score, move = max(moves)
        if (random.randint(0,500) == 222 and
                score <= 3 and
                self._game._comp_player.discarded == False):
            self._game._crib.append(self._game._comp_player.card)
            self._game._comp_player.card = self._game._comp_player.get_card()
            self._game._comp_player.discarded = True
            moves = self._game.move_ai()
            score, move = max(moves)

        space = self._grid.spaces[move]
        space._card = self._game._comp_player.card
        row = space.row
        col = space.col
        self._game._board[row][col] = space._card
        self._game._comp_player.card = self._game._comp_player.get_card()
        if (self._game._comp_player.hand == [] and
                self._game._comp_player.discarded == False):
            self._game._crib.append(self._game._comp_player.card)
            self._game._comp_player.card = None
   

    def draw_scoreboard(self):
        #draw dots
        left = 800
        right = 816
        if self._game._human_player.old_score == 0:
            human1 = BLUE
        else:
            human1 = BLACK
        if self._game._human_player.score == 0:
            human2 = BLUE
        else:
            human2 = BLACK
        if self._game._comp_player.old_score == 0:
            comp1 = RED
        else:
            comp1 = BLACK
        if self._game._comp_player.score == 0:
            comp2 = RED
        else:
            comp2 = BLACK
        pygame.draw.circle(self._screen, human1, (left, 550), 4)
        pygame.draw.circle(self._screen, comp1, (right, 550), 4)
        pygame.draw.circle(self._screen, human2, (left, 560), 4)
        pygame.draw.circle(self._screen, comp2, (right, 560), 4)
        hole_count = 31 
        for idx in xrange(6):
            for idx2 in xrange(5):
                hole_count -= 1 
                #player score col
                if (self._game._human_player.score == hole_count or
                  self._game._human_player.old_score == hole_count):
                    colour = BLUE
                else:
                    colour = BLACK

                pos = (left, (190 + (idx * 60) + (idx2 * 10)))
                pygame.draw.circle(self._screen, colour, pos, 4)
                #computer score col
                if (self._game._comp_player.score == hole_count or
                  self._game._comp_player.old_score == hole_count):
                    colour = RED
                else:
                    colour = BLACK
                pos = (right, (190 + (idx * 60) + (idx2 * 10)))
                pygame.draw.circle(self._screen, colour, pos, 4)
        if self._game._human_player.score == 31:
            colour = BLUE
        elif self._game._comp_player.score == 31:
            colour = RED
        else:
            colour = BLACK
        pygame.draw.circle(self._screen, colour, (808, 170), 4)

    def draw_crib(self, face_up=False):
        """
        draws dealer's crib
        """
        if face_up:
            offset = 25
            idx = 0
            for card in self._game._crib:
                pos = (550 + offset * idx, self._crib_pos[self._game._dealer])
                self._screen.blit(card.image, pos)
                idx += 1
        else:
            offset = 10
            cardsincrib = len(self._game._crib)
            for idx in xrange(cardsincrib):
                pos = (550 + offset * idx, self._crib_pos[self._game._dealer])
                self._screen.blit(self._deck._cardback.image, pos)

    def continue_game(self):
            
            self._grid.clear()
            self._game.switch_dealer()
            if self._game._dealer == 'human':
                pygame.time.wait(500)
                #self._game._cut = False
                self._turn = 'computer'
                self._game._cut = False
                self._game._inprogress = False
                self._game._crib = []
            
            else:
                self._game.deal()
                self._turn  = 'human'
                self._game._cut = True
                
            self._continued = True
            self._scored = False

    def draw_scorescreen(self, player_hands, comp_hands):
        #hand_scores = {'player':[], 'comp':[], 'winner':None, 'score':None,
        #               'human_score':None, 'comp_score':None}
        #
        pygame.draw.line(self._screen, WHITE, (450, 50),(450, 678)) 
        #
        self._screen.blit(self._scorebg, (50, 50))
        text = self._bigfont.render('Player', True, WHITE)
        self._screen.blit(text, (200, 75))
        text = self._bigfont.render('Computer', True, WHITE)
        self._screen.blit(text, (550, 75))
        compy = 465
        playery = 465
        if self._game._dealer == 'human':
            playery = 553
            cribx = 106
        else:
            compy = 553
            cribx = 506
        text = self._bigfont.render('Total', True, WHITE)
        self._screen.blit(text, (106, playery))
        self._screen.blit(text, (506, compy))
        score = str(self.hand_info['human_score'])
        text = self._bigfont.render(score, True, WHITE)
        self._screen.blit(text, (355, playery))
        score =  str(self.hand_info['comp_score'])
        text = self._bigfont.render(score, True, WHITE)
        self._screen.blit(text, (755, compy))
        score = str(self.hand_info['cribscore'])
        text = self._font.render(score, True, WHITE)
        self._screen.blit(text, (cribx + 244, 495))
        
        for idx in xrange(GRID_DIM):
            player_hand = player_hands[idx]
            player_hand_score = str(self.hand_info['player'][idx])
            player_score = str(self.hand_info['human_score'])
            comp_hand = comp_hands[idx]
            comp_hand_score = str(self.hand_info['comp'][idx])
            comp_score = str(self.hand_info['comp_score'])
            winner = self.hand_info['winner']
            winner_score =  str(self.hand_info['score'])
            card_idx = 0 
            for idx2 in xrange(GRID_DIM):
                #blit player card
                pcard = player_hand[card_idx].image
                pcard  = pygame.transform.scale(pcard, (42, 61))
                pos = (106 + idx2 * 46, 110 + idx * 71)
                self._screen.blit(pcard, pos)
                #blit computer card
                ccard = comp_hand[card_idx].image
                ccard = pygame.transform.scale(ccard, (42, 61))
                pos = (506 + idx2 * 46, 110 + idx * 71)
                self._screen.blit(ccard, pos)
                card_idx += 1

            #draw the crib
            text = self._font.render('Crib', True, WHITE)
            self._screen.blit(text, (cribx, 463))
            card = self._game._crib[idx]
            card = pygame.transform.scale(card.image, (42, 61))
            self._screen.blit(card, (cribx + idx * 46, 485))

#            surface = self._scorenumbg.copy()
            text = self._font.render(player_hand_score, True, WHITE)
            width, height =  text.get_size()
#            surface.blit(text, ((surface.get_width() - width) / 2,
#                                 (surface.get_height() - height) / 2))
            self._screen.blit(text, (350, 122 + idx * 71))

            surface = self._scorenumbg.copy()
            text = self._font.render(comp_hand_score, True,
                                     (0,0,0), WHITE)
            width, height =  text.get_size()
            surface.blit(text, ((surface.get_width() - width) / 2,
                                 (surface.get_height() - height) / 2))
            self._screen.blit(surface, (750, 122 + idx * 71))
            score = str(self.hand_info['score'])
            if self.hand_info['winner']:
                text = self.hand_info['winner'] + ' scores ' + score
                text = self._bigfont.render(text, True, WHITE)
                self._screen.blit(text, (206, 625))
            else:
                text = self._bigfont.rende('Round draw', True, WHITE)
                self._screen.blit(text, (206, 625))
            self._screen.blit(self._continue_button, (550, 610))
            text = self._bigfont.render('Continue', True, WHITE)
            textrect = text.get_rect(centerx=self._continue_rect.centerx,
                                     centery=self._continue_rect.centery)
            self._screen.blit(text, textrect)
            pygame.draw.rect(self._screen, WHITE, self._continue_rect, 4)

                
    def score_update(self, player_hands, comp_hands):
        self._scored = True
        self.hand_info = self._game.score_update(player_hands, comp_hands)
    
    def update(self):
        """
        update gamestate and blit screena
        """
        #set grid full boolean to avoid multiple calls to is_full
        full = False
        #blit background and card grid
        self._screen.blit(self._background, self._screen_rect)
        self._screen.blit(self._grid.image, self._grid.rect)
        #draw cardback prior to dealer cut
        if (self._game._dealer == None and not self._game._inprogress):
                self._screen.blit(self._deck._cardback.image,
                                  self._grid.centrespace.rect)
        #draw scoreboard
        self.draw_scoreboard()
        #draw cards to game grid
        for space in self._grid.sprites():
            if space._card:
                self._screen.blit(space._card.image, space.rect)
                
        if self._game._inprogress:
            #draw cut card or card back
            if self._game._cut:
                self._screen.blit(self._game._cutcard.image,
                                  self._grid.centrespace.rect)
            else:
                self._screen.blit(self._deck._cardback.image,
                                  self._grid.centrespace.rect)
            #draw players' hands
            self.draw_hands()

            #draw crib face down or up if grid full
            if self._grid.is_full():
                self.draw_crib(True)
                full = True
            else:
                self.draw_crib()
                

            #check for hover over discard card    
            if not self._game._human_player.discarded:
                self.check_hover()

            #call ai move if needed
            if self._turn is 'computer' and self._game._cut:
                if self._game._comp_player.card: 
                    self.move_ai()
                    self._turn = 'human' 

        elif self._game._dealer == 'human':
            text = self._bigfont.render('Deal', True, BLACK)
            textrect = text.get_rect(centerx=self._deal_rect.centerx,
                                     centery=self._deal_rect.centery)
            self._screen.blit(text, textrect)
            pygame.draw.rect(self._screen, BLACK, self._deal_rect, 4)
                         

        #if grid is full auto discard last card switch tur n if necessary.
        #update score function and draw scorescreen until game continued
        if full:         
            if self._game._human_player.card:
                self._game.crib_discard(self._game._human_player)
                    
            if self._game._comp_player.card:
                self._turn = 'computer'
                self.move_ai()
                
            player_hands =  [row for row in self._game._board]
            comp_hands = self._game.get_cols(self._game._board)

            if not self._scored:
               self.score_update(player_hands, comp_hands)
            self.draw_scorescreen(player_hands, comp_hands)
                    
    def main(self):
        """
        main game loop
        """
        
        clock = pygame.time.Clock()
        while 1:
            #update display at 60fps
            clock.tick(30)
            #process input events
            self.process_events()
            #blit screen and update gamstate(calls ai move function) 
            self.update()
            #flip screen
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
        self.centrespace = None
        self.spaces = {}
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
                self.spaces[(row, col)] = space
                if row == 2 and col == 2:
                    self.centrespace = space
    def clear(self):
        """
        clear grid
        """
        for space in self.sprites():
            space._card = None

    def is_full(self):
        """
        check ifn grid is full
        """
        spaces = [space for space in self.sprites() if space._card is None]
        spaces.remove(self.centrespace)
        if not spaces:
            return True
        
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
                left = CARD_WIDTH * (card_num - 1)
                top = CARD_HEIGHT * self._suits.index(suit)
                rect = (left, top, CARD_WIDTH, CARD_HEIGHT)
                image = self._cards_sprite.subsurface(rect)
                rect = image.get_rect()
                card = Card(card_num, suit, image, rect)
                self._cards[str(card)] = card
                self.add(card)
        #card back last row, col = 4,1
        subrect = CARD_WIDTH, CARD_HEIGHT * 4, CARD_WIDTH, CARD_HEIGHT
        image = self._cards_sprite.subsurface(subrect)
        rect = image.get_rect()
        self._cardback = Card(14, 'cardback', image, rect)
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
        self.cardnum = card
        self._card = str(card)+suit
        if card > 10:
            self.value = 10
        else:
            self.value = card 
  
    def __str__(self):
        return str(self._card) 
    
gui = CrossCribGUI()
