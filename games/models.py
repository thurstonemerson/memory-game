"""
The class definitions for the Datastore entities used in the game service. 
Created on 18/03/2016

@author: thurstonemerson
"""

from protorpc import messages
from google.appengine.ext import ndb

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
    
class Match(ndb.Model):
    """Score object"""
    date = ndb.DateProperty(required=True)
    winner = ndb.KeyProperty(required=True)
    loser = ndb.KeyProperty(required=True)

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
        return "{0}:{1}".format(self.card_name.name, self.flipped)    
       
    def __str__(self):
        return "{0}:{1}".format(self.card_name.name, self.flipped)   
    

