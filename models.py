"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
import math
import logging
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb




class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()

# class Tile(ndb.Model):
#     """Tile object"""
#     flipped = ndb.BooleanProperty(required=True, default=False)
#     
#     @classmethod
#     def flip():
#         flipped = not flipped
        

class Game(ndb.Model):
    """Game object"""
    board = ndb.PickleProperty(required=True)
    next_move = ndb.KeyProperty(required=True) # The User's whose turn it is
    first_user = ndb.KeyProperty(required=True, kind='User')
    second_user = ndb.KeyProperty(required=True, kind='User')
    game_over = ndb.BooleanProperty(required=True, default=False)
    winner = ndb.KeyProperty()
    history = ndb.PickleProperty(required=True)
    grid = []

    @classmethod
    def new_game(self, first_user, second_user):
        """Creates and returns a new game"""
        game = Game(first_user=first_user,
                    second_user=second_user,
                    next_move=first_user)
        deck = game.make_carddeck()
        game.board = game.make_gridboard(deck)
        game.history = []
        game.put()
        return game
    
    def make_carddeck(self):
        """"create a deck of cards with two of each card"""
        deck = []
        for name in CardNames:
            card = Card(card_name=name)
            deck.append(card)
            deck.append(card)
            
        logging.info("Completed building card deck {0}".format(deck))
        return deck
    
    def make_gridboard(self, deck):
        """"make a gridboard from a deck of cards with random placement"""
        griddimension = int(math.sqrt(len(deck)))
        gridboard = [[self.remove_random_card_from_deck(deck) for row in range(griddimension)] for col in range(griddimension)]
        logging.info("Completed building grid board {0}".format(gridboard))
        return gridboard
    
    def remove_random_card_from_deck(self, deck):
        """Select and return a random card, removing it from the deck"""
        card = random.choice(deck)
        deck.remove(card)
        return card

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.first_user = self.first_user.get().name
        form.second_user = self.second_user.get().name
        form.game_over = self.game_over
        form.message = message
        return form

#     def end_game(self, winner):
#         """Ends the game"""
#         self.winner = winner
#         self.game_over = True
#         self.put()
#         loser = self.user_o if winner == self.user_x else self.user_x
#         # Add the game to the score 'board'
#         score = Score(date=date.today(), winner=winner, loser=loser)
#         score.put()
# 
#         # Update the user models
#         winner.get().add_win()
#         loser.get().add_loss()


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    first_user = messages.StringField(5, required=True)
    second_user = messages.StringField(6, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    first_user = messages.StringField(1, required=True)
    second_user = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
    

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
    
class Card():
    """"A card used in the deck of cards"""
    def __init__(self, card_name):
        self.card_name = card_name
        self.flipped = False
    
    def flip(self):
        self.flipped = not self.flipped
    
    def __repr__(self):
        return self.card_name.name    
       
    def __str__(self):
        return self.card_name.name
    

