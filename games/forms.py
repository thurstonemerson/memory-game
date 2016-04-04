'''
Created on 18/03/2016

Forms to be used when interacting with the game module of the memory api

@author: thurstonemerson
'''
from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
    next_move = messages.StringField(3, required=True)
    game_over = messages.BooleanField(4, required=True)
    unmatched_pairs = messages.IntegerField(5, required=True)
    first_user_score = messages.IntegerField(6, required=True)
    second_user_score = messages.IntegerField(7, required=True)
    message = messages.StringField(8, required=True)
    winner = messages.StringField(9)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    first_user = messages.StringField(1, required=True)
    second_user = messages.StringField(2, required=True)
    
class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    winner_score = messages.IntegerField(1, required=True)
    loser_score = messages.IntegerField(2, required=True)
    winner = messages.StringField(3, required=True)
    loser = messages.StringField(4, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    name = messages.StringField(1, required=True)
    row = messages.IntegerField(2, required=True)
    column = messages.IntegerField(3, required=True)
    
class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)
    