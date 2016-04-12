"""
The class definitions for the Datastore entities used in the game service. 
Created on 18/03/2016

@author: thurstonemerson
"""

from protorpc import messages
from google.appengine.ext import ndb
from config import DEBUG

class Game(ndb.Model):
    """Game object"""
    board = ndb.PickleProperty(required=True)
    next_move = ndb.KeyProperty(required=True) # The User's whose turn it is
    first_user = ndb.KeyProperty(required=True, kind='User')
    second_user = ndb.KeyProperty(required=True, kind='User')
    first_user_score = ndb.IntegerProperty(default=0)
    second_user_score = ndb.IntegerProperty(default=0)
    unmatched_pairs = ndb.IntegerProperty(default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    loser = ndb.KeyProperty()
    firstGuess = ndb.PickleProperty()
    secondGuess = ndb.PickleProperty()
    history = ndb.PickleProperty(required=True)
    
class Score(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    winner = ndb.KeyProperty(required=True)
    loser = ndb.KeyProperty(required=True)
    winner_score = ndb.IntegerProperty(default=0)
    loser_score = ndb.IntegerProperty(default=0)

class CardNames(messages.Enum):
    """The names of the cards to be used in the memory game"""
    DEATH = 1
    TEMPERANCE = 2
    HIGH_PRIESTESS = 3
    HERMIT = 4
    HANGED_MAN = 5
    LOVERS = 6
    JUSTICE = 7
    FOOL = 8

class Turn():
    """"A user's turn in the game of memory"""
    def __init__(self, user, first_guess, second_guess, match_made):
        self.user = user
        self.first_guess = first_guess
        self.second_guess = second_guess
        self.match_made = match_made
        
    def __repr__(self):
        return "{0}:{1}:{2}:{3}".format(self.user, self.first_guess, self.second_guess, self.match_made)    
       
    def __str__(self):
        return "{0}:{1}:{2}:{3}".format(self.user, self.first_guess, self.second_guess, self.match_made)    
         
class Move():
    """"A single move in the game of memory"""
    def __init__(self, card, row, column):
        self.card = card
        self.row = row
        self.col = column
        
    def __repr__(self):
        return "{0}:{1}:{2}".format(self.card.card_name, self.row, self.col)    
       
    def __str__(self):
        return "{0}:{1}:{2}".format(self.card.card_name, self.row, self.col)  
    
class Card():
    """"A card used in the deck of cards"""
    def __init__(self, card_name):
        self.card_name = card_name
        self.flipped = False
        
    def reset(self):
        self.flipped = False
    
    def flip(self):
        self.flipped = not self.flipped
    
    def __repr__(self):
        if DEBUG:
            return "{0}:{1}".format(self.card_name.name, self.flipped)
        else:    
            return "{0}".format(self.card_name if self.flipped else "XXX")
        
    def __str__(self):
        if DEBUG:
            return "{0}:{1}".format(self.card_name.name, self.flipped)
        else:    
            return "{0}".format(self.card_name if self.flipped else "XXX")
    

