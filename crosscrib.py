#!/usr/bin/env python

import random
from itertools import combinations

#size constants
GRID_SIZE = 5

class CrossCrib:
    """
    CrossCrib game
    """

    def __init__(self, deckofcards):
        self._board = [[None for idx in xrange(GRID_SIZE)]
                             for idx in xrange(GRID_SIZE)]
        self._human_player = Player()
        self._comp_player = Player()
        self._crib = []
        self._dealer = None
        self._inprogress = False
        self._gameover = False
        self._winner = None
        #Card deck is not created until gui is instantiated
        #at which point the deck is passed to the game object
        self._cards = deckofcards.sprites()

    def __str__(self):
        return str(self._board)

    def clone_board(self):
        board = []
        for row in self._board:
                board.append(row[:])
        return board
    def get_card(self, row, col):
        """
        get card at grid position
        """

        return self._board[row][col]

    def set_card(self, row, col, card):
        """
        set card at grid position
        """

        self._board[row][col] =  card

    def deal(self):
        """
        deal cards
        """
        self._board = [[None for idx in xrange(GRID_SIZE)]
                             for idx in xrange(GRID_SIZE)]
        random.shuffle(self._cards)
        self._human_player.hand = self._cards[:13]
        self._human_player.card = self._human_player.get_card()
        self._human_player.discarded = False
        self._comp_player.discarded = False
        self._comp_player.hand = self._cards[13:26]
        self._comp_player.card = self._comp_player.get_card()
        self._cutcard = random.choice(self._cards[30:])
        self._board[2][2] = self._cutcard
        self._crib = self._cards[28:30]
        self._inprogress = True
        self._cut = False

    def cut_for_deal(self):
        #return comp, human
        cards = self._cards[:]
        comp = random.choice(cards)
        human = random.choice(cards)
        return comp, human
    
    def reset(self):
        self._board = [[None for idx in xrange(GRID_SIZE)]
                             for idx in xrange(GRID_SIZE)]
        self._human_player = Player()
        self._comp_player = Player()
        self._cutcard = None
        self._cut = False
        self._dealer = None
        self._inprogress = False
        self._gameover = False
        self._winner = None
        
    def score_hand(self, hand, check_jack=False):
        #check for pairs, triplets and quadruplets
        score = 0
        hand = filter(None, hand)
        handnums =  [card.cardnum for card in hand]
        suits = [card.suit for card in hand]
        values = [card.value for card in hand]
        
        #add pairs, triplets and quadruplets
        score += self.score_pairs(handnums[:])
        score += self.score_runs(handnums[:])
        score += self.score_fifteens(values)
        if check_jack:
            hand.remove(self._cutcard)
            for card in hand:
                if card.cardnum == 11 and card.suit == self._cutcard.suit:
                    score +=1
            
        return score

    def score_fifteens(self, hand):
        hand.sort()
        score = 0 
        for combo in combinations(hand, 2):
            if sum(combo) == 15:
                score += 2
        for combo in combinations(hand, 3):
            if sum(combo) == 15:
                score += 2
        for combo in combinations(hand, 4):
            if sum(combo) == 15:
                score += 2
        if sum(hand) == 15:
            score += 2
        return score
    
    def score_runs(self, hand):
        hand_set = set(hand)
        hand_set = list(hand_set)
        hand_set.sort()
        count = 1
        run = []
        score = 0
        combos = []
            
        for idx in xrange(len(hand_set)-1):
            if hand_set[idx] + 1 == hand_set[idx + 1]:
                count += 1
                run.append(hand_set[idx])
            else:
                if count >= 3:
                    score += count
                    for card in run:
                        score *= hand.count(card)
                    count = 1
                    run = []

                run = []
                count = 1
                
            if idx == len(hand_set) - 2 and count >= 3:
                score += count
                for card in run:
                    score *= hand.count(card)
        return score
    
        
    def score_pairs(self, hand):
        score = 0 
        for card in hand:
            if hand.count(card) == 4:
                score += 12
                break
            
            elif hand.count(card) == 3:
                score += 6
                hand =  filter(lambda new_card: new_card is not card, hand)
                
            elif hand.count(card) == 2:
                score += 2
                hand = filter(lambda new_card: new_card is not card, hand)
                
        return score

    def score_update(self, player_hands, comp_hands):
        idx = 0
        player_score = 0
        comp_score = 0
        hand_scores = {'player':[], 'comp':[], 'winner':None, 'score':None,
                       'human_score':None, 'comp_score':None, 'cribscore':None}
        for hand in player_hands:
            if idx == 2:
                score = self.score_hand(hand, check_jack=True)
                player_score += score
                hand_scores['player'].append(score)
                score = self.score_hand(comp_hands[idx], check_jack=True)
                comp_score += score
                hand_scores['comp'].append(score)
                idx += 1
            else:
                score = self.score_hand(hand)
                player_score += score
                hand_scores['player'].append(score)
                score = self.score_hand(comp_hands[idx])
                comp_score += score
                hand_scores['comp'].append(score)
                idx += 1
                
        self._crib.append(self._cutcard)
        
        hand_scores['cribscore'] = self.score_hand(self._crib)

        if self._dealer == 'human':
            player_score += hand_scores['cribscore']
        else:
            comp_score += hand_scores['cribscore']

        dif = player_score - comp_score
        hand_scores['human_score'] = player_score
        hand_scores['comp_score'] = comp_score
        if dif > 0:
            score = self._human_player.score
            self._human_player.old_score = score
            self._human_player.score += dif
            hand_scores['winner'] = 'You'
            hand_scores['score'] = dif
            if self._human_player.score >= 31:
                self._human_player.score = 31
                self._gameover = True
                self._winner = 'human'
                self._inprogress = False
        elif dif < 0:
            score = self._comp_player.score
            self._comp_player.old_score = score
            self._comp_player.score += abs(dif)
            hand_scores['winner'] = 'Computer'
            hand_scores['score'] = abs(dif)
            if self._comp_player.score >= 31:
                self._comp_player.score = 31
                self._gameover = True
                self._winner = 'computer'
                self._inprogress = False

        return hand_scores
    
    def get_cols(self, board):
        cols = [[None for col in xrange(GRID_SIZE)]
                    for col in xrange(GRID_SIZE)]
        for col in xrange(GRID_SIZE):
            for row in xrange(GRID_SIZE):
                cols[col][row] = board[row][col]
        return cols

    def switch_dealer(self):
        if self._dealer == 'human':
            self._dealer = 'computer'
        else:
            self._dealer = 'human'


    def get_cols(self, board):
        cols = [[None for col in xrange(GRID_SIZE)]
                    for col in xrange(GRID_SIZE)]
        for col in xrange(GRID_SIZE):
            for row in xrange(GRID_SIZE):
                cols[col][row] = board[row][col]
        return cols

    def switch_dealer(self):
        if self._dealer == 'human':
            self._dealer = 'computer'
        else:
            self._dealer = 'human'

    def crib_discard(self, player):
        self._crib.append(player.card)
        player.card = player.get_card()
        player.discarded = True
        
    def move_ai(self):
        empty_spaces = [(row, col) for row in xrange(GRID_SIZE)
                            for col in xrange(GRID_SIZE) if
                            self._board[row][col] == None and
                            ((row, col) != (2, 2))]
        moves = []
        
        for space in empty_spaces:
            board = self.clone_board()
            
            row, col = space
            board[row][col] = self._comp_player.card
  
            #computer columns
            cols = self.get_cols(board)
            # player rows
            rows = board

            comp_score = 0
            player_score = 0
            for idx in xrange(GRID_SIZE):
                if idx == 2:
                    check_jack = True
                else:
                    check_jack = False

                comp_score += self.score_hand(cols[idx], check_jack)
                player_score += self.score_hand(rows[idx], check_jack)
            move_score = comp_score - player_score
            moves.append((move_score, space))
        #score, move = max(moves)

        return moves    
        

class Player:
    """
    crib player
    """

    def __init__(self):
        self.hand = []
        self.card = None
        self.movecount = 0
        self.discarded = False
        self.score =  0
        self.old_score = 0
        
    def get_card(self):
        if self.hand:
            return self.hand.pop()
        else:
            return None

    def next_card(self):
        self.card = self.get_card()

