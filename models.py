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
    firstGuess = ndb.PickleProperty()
    secondGuess = ndb.PickleProperty()
    
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
            cardOne = Card(card_name=name)
            cardTwo = Card(card_name=name)
            deck.append(cardOne)
            deck.append(cardTwo)
            
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
    
    def reset_gridboard(self):
        """Take the cards moved in the first and second guess and reset to not flipped"""
        card = self.board[self.firstGuess.row][self.firstGuess.col]
        card.reset()
        card = self.board[self.secondGuess.row][self.secondGuess.col]
        card.reset()
         
    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=self.key.urlsafe(),
                        board = str(self.board),
                        first_user=self.first_user.get().name,
                        second_user=self.second_user.get().name,
                        next_move=self.next_move.get().name,
                        game_over=self.game_over,
                        message=message)
        #if self.winner:
        #    form.winner = self.winner.get().name
        return form
    
    def make_move(self, row, column, first_user):
        """Make a move on the gridboard by flipping the card located at the row and column"""

        #First flip the card
        self.board[row][column].flip()
 
        #Make the first guess of this turn
        if self.firstGuess is None or self.secondGuess is not None:
 
            self.make_first_guess(row, column)
            message = "One more guess to make"
 
        else: #Make the second guess of this turn
 
            #If the second guess returns true, we have made a match
            if self.make_second_guess(row, column) == True:
                #unmatchedPairs--
                #message = (this.unmatchedPairs > 0) ? "You made a match" : "You won the game";
                message = "You made a match"
            else: #We didn't make a match, so it is the other players turn
                self.next_move = self.second_user if first_user else self.first_user
                message = "Not a match"
        
        self.put()
        return message
        
    def make_first_guess(self, row, column):
        """Make a first guess on the gridboard at the specified row and column"""
        logging.info("First guess: {0}, Second guess : {1}".format(self.firstGuess, self.firstGuess))
        
         #reset the gridboard to start a new guess
        if self.secondGuess is not None:
            self.reset_gridboard()
            self.firstGuess = self.secondGuess = None
             
        #you have made a first guess, you have one more guess to make
        self.firstGuess = Move(self.board[row][column], row, column)
        
    def make_second_guess(self, row, column):
        """Make a second guess on the gridboard at the specified row and column
        Return true if the second guess was a match"""
        logging.info("First guess: {0}, Second guess : {1}".format(self.firstGuess, self.firstGuess))
        
         #If the first guess matches the selected tile, we have a match
        if self.firstGuess.card.card_name == self.board[row][column].card_name:
                #unmatchedPairs--
                #message = (this.unmatchedPairs > 0) ? "You made a match" : "You won the game";
                self.firstGuess = self.secondGuess = None
                return True
        
        self.secondGuess = Move(self.board[row][column], row, column)
        return False

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
    board = messages.StringField(2, required=True)
    first_user = messages.StringField(3, required=True)
    second_user = messages.StringField(4, required=True)
    next_move = messages.StringField(5, required=True)
    game_over = messages.BooleanField(6, required=True)
    message = messages.StringField(7, required=True)
    #winner = messages.StringField(7)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    first_user = messages.StringField(1, required=True)
    second_user = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    user_name = messages.StringField(1, required=True)
    row = messages.IntegerField(2, required=True)
    column = messages.IntegerField(3, required=True)

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
    

