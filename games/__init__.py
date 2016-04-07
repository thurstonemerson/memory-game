'''
Created on 18/03/2016

Game service module, where all the logic of game creation and making moves on the gridboard 
is contained. Persistence is dealt with in the service.

@author: thurstonemerson
'''
from models import Game, CardNames, Card, Move, Score
from forms import GameForm, ScoreForm
from core import Service
from google.appengine.ext import ndb
from datetime import date
import logging
import math
import random
import endpoints

class ScoreService(Service):
    """Service class interacting with the Score datastore"""
    __model__ = Score
    
    #-----------------------------------------------------------------------
    #Create a new score on the scoreboard
    #-----------------------------------------------------------------------
    
    def new_score(self, winner, loser, first_user_score, second_user_score):
        """Creates and returns a new score, persisting to the google datastore"""
       
        if first_user_score == second_user_score:
                raise endpoints.BadRequestException('Score cannot be created, game was a draw')
         
        #create a new score and initialise with winner/loser deatils
        score = super(ScoreService, self).new()
        data = {"date": date.today(), "winner": winner, "loser": loser, 
               "winner_score": first_user_score if first_user_score > second_user_score else second_user_score, 
               "loser_score": first_user_score if first_user_score < second_user_score else second_user_score}
         
        super(ScoreService, self).update(score, **data)
        return score
    
    #-----------------------------------------------------------------------
    #Return a list of scores from the specified user
    #-----------------------------------------------------------------------
  
    
    def get_user_scores(self, user):
        """Returns a list of scores by the requested user"""
        scores = Score.query(ndb.OR(Score.winner == user.key,
                                    Score.loser == user.key)).fetch()
        return scores
    
    #-----------------------------------------------------------------------
    #Create a form from a score
    #-----------------------------------------------------------------------
  

    def to_form(self, score):
        """Returns a ScoreForm representation of the Score"""
        form = ScoreForm(date=str(score.date),
                         winner=score.winner.get().name,
                         loser=score.loser.get().name,
                         winner_score=score.winner_score,
                         loser_score=score.loser_score)
        return form

class GamesService(Service):
    """Service class interacting with the Game datastore"""
    __model__ = Game
    
    #-----------------------------------------------------------------------
    #Return a list of active games from the specified user
    #-----------------------------------------------------------------------
  
    def get_user_games(self, user):
        """Returns a list of active games by the requested user"""
        games = Game.query(ndb.OR(Game.first_user == user.key,
                                  Game.second_user == user.key)).filter(Game.game_over == False).fetch()
        return games
    
        
    #-----------------------------------------------------------------------
    #Creation of a new game of memory
    #-----------------------------------------------------------------------
   
    def new_game(self, first_user, second_user):
        """Creates and returns a new game, persisting to the google datastore"""
        deck = self._make_carddeck()
        
        #create a new game model and initialise with user details, gridboard
        game = super(GamesService, self).new()
        data = {"first_user": first_user, "second_user": second_user, 
               "board": self._make_gridboard(deck), 
               "unmatched_pairs": len(CardNames), "next_move": first_user}
         
        super(GamesService, self).update(game, **data)
          
        return game
    
    #-----------------------------------------------------------------------
    #Private methods handling creation of card deck and gridboard
    #-----------------------------------------------------------------------
    
    def _make_carddeck(self):
        """"create a deck of cards with two of each card"""
        deck = []
        for name in CardNames:
            cardOne = Card(card_name=name)
            cardTwo = Card(card_name=name)
            deck.append(cardOne)
            deck.append(cardTwo)
            
        logging.info("Completed building card deck {0}".format(deck))
        return deck
    
    def _make_gridboard(self, deck):
        """"make a gridboard from a deck of cards with random placement"""
        griddimension = int(math.sqrt(len(deck)))
        gridboard = [[self._remove_random_card_from_deck(deck) for row in range(griddimension)] for col in range(griddimension)]
        logging.info("Completed building grid board {0}".format(gridboard))
        return gridboard
    
    def _remove_random_card_from_deck(self, deck):
        """Select and return a random card, removing it from the deck"""
        card = random.choice(deck)
        deck.remove(card)
        return card
    
    #-----------------------------------------------------------------------
    #Validating a requested move on the gridboard
    #-----------------------------------------------------------------------
    
    def is_valid_move(self, game, row, column, raise_error=True):
        """Check the requested move is valid. Optionally raise an exception if invalid"""
         
        # Check that the requested location is actually on the gridboard
        if not self._is_on_gridboard(game, row, column):
            if raise_error:
                raise endpoints.BadRequestException('Requested move is out of grid board boundary')
            else:
                return False
         
        # Check that the card has not already been flipped    
        if game.board[row][column].flipped:
            if raise_error:
                raise endpoints.BadRequestException('Card has already been flipped')
            else:
                return False
        
        return True
    
    #-----------------------------------------------------------------------
    #Private methods handling validation of moves on the gridboard
    #-----------------------------------------------------------------------
  
    
    def _get_max_row_number(self, game):
        """Returns the maximum row number allowed for the gridboard"""
        logging.info("Maximum gridboard row number: {0}".format(len(game.board)-1)) 
        return len(game.board)-1
    
    def _get_max_col_number(self, game):
        """Returns the maximum column number allowed for the gridboard"""
        if self._get_max_row_number(game) >= 0:
            logging.info("Maximum gridboard col number: {0}".format(len(game.board[0])-1))
            return len(game.board[0])-1
        return 0
    
    def _is_on_gridboard(self, game, row, column):
        """Check if the requested move is actually on the gridboard"""
        if row < 0 or row > self._get_max_row_number(game):
            return False
        if column < 0 or column > self._get_max_col_number(game):
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
 
            self._make_first_guess(game, row, column)
            message = "One more guess to make"
 
        else: #Make the second guess of this turn
 
            #If the second guess returns true, we have made a match
            if self._make_second_guess(game, row, column) == True:
                #add one to the user score
                self._increment_score(game, first_user)
                #decrement the number of card pairs left to find
                game.unmatched_pairs-=1
                #Check to see if the game has been completed
                if game.unmatched_pairs == 0:
                    #check who has the highest score and assign a winner
                    self._assign_winner(game)
                    message = "Game over"
                else:
                    message = "You made a match"
            else: #We didn't make a match, so it is the other players turn
                game.next_move = game.second_user if first_user else game.first_user
                message = "Not a match"
        
        super(GamesService, self).save(game)
        
        return message
    
    #-----------------------------------------------------------------------
    #Private methods handling move making on the gridboard
    #-----------------------------------------------------------------------
    
    def _increment_score(self, game, first_user):
        """Increment the score for a particular user"""
        if first_user:
            game.first_user_score += 1
        else:
            game.second_user_score += 1    
            
    def _assign_winner(self, game):
        """Check the scores and assign the winning user"""
        game.game_over = True

        if game.first_user_score > game.second_user_score:
            game.winner = game.first_user
            game.loser = game.second_user  
        elif game.first_user_score < game.second_user_score: 
            game.winner = game.second_user
            game.loser = game.first_user
        
        #otherwise it's a draw, winner remains None
            
        
    def _make_first_guess(self, game, row, column):
        """Make a first guess on the gridboard at the specified row and column"""
        logging.info("First guess: {0}, Second guess : {1}".format(game.firstGuess, game.firstGuess))
        
        #reset the gridboard to start a new guess
        if game.secondGuess is not None:
            self._reset_gridboard(game)
            game.firstGuess = game.secondGuess = None
             
        #you have made a first guess, you have one more guess to make
        game.firstGuess = Move(game.board[row][column], row, column)
        
    def _make_second_guess(self, game, row, column):
        """Make a second guess on the gridboard at the specified row and column
        Return true if the second guess was a match"""
        logging.info("First guess: {0}, Second guess : {1}".format(game.firstGuess, game.firstGuess))
        
        #If the first guess matches the selected tile, we have a match
        if game.firstGuess.card.card_name == game.board[row][column].card_name:
                game.firstGuess = game.secondGuess = None
                return True
        
        game.secondGuess = Move(game.board[row][column], row, column)
        return False
    
    
    def _reset_gridboard(self, game):
        """Take the cards moved in the first and second guess and reset to not flipped"""
        card = game.board[game.firstGuess.row][game.firstGuess.col]
        card.reset()
        card = game.board[game.secondGuess.row][game.secondGuess.col]
        card.reset()
    
    #-----------------------------------------------------------------------
    #Initialising a form object to return to the user
    #-----------------------------------------------------------------------
    
    def to_form(self, game, message=""):
        """Returns a GameForm representation of the Game"""
        form = GameForm(urlsafe_key=game.key.urlsafe(),
                        board = str(game.board),
                        next_move=game.next_move.get().name,
                        game_over=game.game_over,
                        message=message,
                        first_user_score=game.first_user_score,
                        second_user_score=game.second_user_score,
                        unmatched_pairs=game.unmatched_pairs)
        if game.winner:
            form.winner = game.winner.get().name
        return form
