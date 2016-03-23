'''
Created on 18/03/2016

Game service module, where all the logic of game creation and making moves on the gridboard 
is contained. Persistence is dealt with in the service.

@author: thurstonemerson
'''
from models import Game, CardNames, Card, Move
from forms import GameForm
from core import Service
import logging
import math
import random
import endpoints

class GamesService(Service):
    __model__ = Game

    def new_game(self, first_user, second_user):
        """Creates and returns a new game, persisting to the google datastore"""
        deck = self.make_carddeck()
        
        #create a new game model and initialise with user details, gridboard
        game = super(GamesService, self).new()
        data = {"first_user": first_user, "second_user": second_user, 
               "board": self.make_gridboard(deck), "history": [], 
               "unmatched_pairs": len(CardNames), "next_move": first_user}
         
        super(GamesService, self).update(game, **data)
          
        return game
    
    #-----------------------------------------------------------------------
    #Creation of card deck and gridboard
    #-----------------------------------------------------------------------
    
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
    
    #-----------------------------------------------------------------------
    #Validating a requested move on the gridboard
    #-----------------------------------------------------------------------
    
    def is_valid_move(self, game, row, column, raise_error=True):
        """Check the requested move is valid. Optionally raise an exception if invalid"""
        is_on_gridboard = self.is_on_gridboard(game, row, column)
         
        # Check that the requested location is actually on the gridboard
        if not is_on_gridboard and raise_error:
            raise endpoints.BadRequestException('Requested move is out of grid board boundary')
         
        is_flipped = game.board[row][column].flipped
         
        # Check that the card has not already been flipped    
        if is_flipped and raise_error:
            raise endpoints.BadRequestException('Card has already been flipped')
        
        return (is_on_gridboard and is_flipped)
    
    
    def get_max_row_number(self, game):
        """Returns the maximum row number allowed for the gridboard"""
        logging.info("Maximum gridboard row number: {0}".format(len(game.board)-1)) 
        return len(game.board)-1
    
    def get_max_col_number(self, game):
        """Returns the maximum column number allowed for the gridboard"""
        if self.get_max_row_number(game) >= 0:
            logging.info("Maximum gridboard col number: {0}".format(len(game.board[0])-1))
            return len(game.board[0])-1
        return 0
    
    def is_on_gridboard(self, game, row, column):
        """Check if the requested move is actually on the gridboard"""
        if row < 0 or row > self.get_max_row_number(game):
            return False
        if column < 0 or column > self.get_max_col_number(game):
            return False
        return True
    
    #-----------------------------------------------------------------------
    #Making an actual move on a grid board
    #-----------------------------------------------------------------------
    
    def make_move(self, game, row, column, first_user):
        """Make a move on the gridboard by flipping the card located at the row and column"""

        #First flip the card
        game.board[row][column].flip()
 
        #Make the first guess of this turn
        if game.firstGuess is None or game.secondGuess is not None:
 
            self.make_first_guess(game, row, column)
            message = "One more guess to make"
 
        else: #Make the second guess of this turn
 
            #If the second guess returns true, we have made a match
            if self.make_second_guess(game, row, column) == True:
                #self.unmatchedPairs--
                #message = (this.unmatchedPairs > 0) ? "You made a match" : "Game over";
                message = "You made a match"
            else: #We didn't make a match, so it is the other players turn
                game.next_move = game.second_user if first_user else game.first_user
                message = "Not a match"
        
        super(GamesService, self).save(game)
        
        return message
        
    def make_first_guess(self, game, row, column):
        """Make a first guess on the gridboard at the specified row and column"""
        logging.info("First guess: {0}, Second guess : {1}".format(game.firstGuess, game.firstGuess))
        
        #reset the gridboard to start a new guess
        if game.secondGuess is not None:
            self.reset_gridboard(game)
            game.firstGuess = game.secondGuess = None
             
        #you have made a first guess, you have one more guess to make
        game.firstGuess = Move(game.board[row][column], row, column)
        
    def make_second_guess(self, game, row, column):
        """Make a second guess on the gridboard at the specified row and column
        Return true if the second guess was a match"""
        logging.info("First guess: {0}, Second guess : {1}".format(game.firstGuess, game.firstGuess))
        
        #If the first guess matches the selected tile, we have a match
        if game.firstGuess.card.card_name == game.board[row][column].card_name:
                game.firstGuess = game.secondGuess = None
                return True
        
        game.secondGuess = Move(game.board[row][column], row, column)
        return False
    
    
    def reset_gridboard(self, game):
        """Take the cards moved in the first and second guess and reset to not flipped"""
        card = game.board[game.firstGuess.row][game.firstGuess.col]
        card.reset()
        card = game.board[game.secondGuess.row][game.secondGuess.col]
        card.reset()
    
    #-----------------------------------------------------------------------
    #Initialising a form object to return to the user
    #-----------------------------------------------------------------------
    
    def to_form(self, game, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=game.key.urlsafe(),
                        board = str(game.board),
                        next_move=game.next_move.get().name,
                        game_over=game.game_over,
                        message=message)
        #if self.winner:
        #    form.winner = self.winner.get().name
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