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
        deck = game.make_deck()
        game.board = game.make_grid(deck)
        game.history = []
        game.put()
        return game
    
    def make_deck(self):
        """"create a deck of cards with two of each tile"""
        deck = []
        for title in TileTitles:
            deck.append(title)
            deck.append(title)
            
        logging.info("Completed deck {0}".format(deck))
        return deck
    
    def make_grid(self,deck):
        """"make a randomly placed grid from a deck of tiles"""
        gridDimension = int(math.sqrt(len(deck)))
        gridboard = []
        
        for x in range(gridDimension):
            row = []
            for y in range(gridDimension):
                tile = random.choice(deck)
                row.append(tile)
                logging.info("Setting grid{0}{1} to {2}".format(x, y, tile))
                deck.remove(tile)
            gridboard.append(row)
            
        logging.info("Completed grid {0}".format(gridboard))
        return gridboard

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
    
#     @classmethod
#     def flip():
#         flipped = not flipped



class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
    

class TileTitles(messages.Enum):
    """The title of tiles to be used in the memory game"""
    EIGHT_BALL = 1
    KRONOS = 2
    BAKED_POTATO = 3
    DINOSAUR = 4
    ROCKET= 5
    SKINNY_UNICORN = 6
    THAT_GUY = 7
    ZEPPELIN = 8
