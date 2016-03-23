'''
Created on 18/03/2016

Forms to be used when interacting with the game module of the memory api

@author: thurstonemerson
'''
from protorpc import messages

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    board = messages.StringField(2, required=True)
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
    name = messages.StringField(1, required=True)
    row = messages.IntegerField(2, required=True)
    column = messages.IntegerField(3, required=True)
    