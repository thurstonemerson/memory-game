'''
Created on 18/03/2016

Game api concerned primarily with communicating to/from the api's users. Contains
api endpoints to create and find a game, and make a move in a game of memory.
Game logic and persistence is manipulated in the games service module.

@author: thurstonemerson
'''

import endpoints
from protorpc import remote, messages
from api import memory_api

from forms import NewGameForm, GameForm, GameForms, MakeMoveForm

from services import games, users 

USER_REQUEST = endpoints.ResourceContainer(name=messages.StringField(1),
                                           email=messages.StringField(2))
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)


@memory_api.api_class(resource_name='games', path='games')
class GameApi(remote.Service):
    """Memory game API for requesting creation of and finding a game, as well as making
    a move on the gridboard"""

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates a new game of memory for two users"""
        first_user = users.get_by_name(request.first_user)
        second_user = users.get_by_name(request.second_user)
        if not first_user and second_user:
            raise endpoints.NotFoundException(
                    'One of users with that name does not exist!')
        if first_user.key == second_user.key:
            raise endpoints.NotFoundException(
                    'Please select two different users to play this game!')

        game = games.new_game(first_user.key, second_user.key)

        return games.to_form(game, 'Good luck playing Memory, it\'s {0}\'s turn first!'.format(first_user.name))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = games.get_by_urlsafe(request.urlsafe_game_key)
        if game:
            return games.to_form(game, 'Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')
 
    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move on the grid board. Returns a game state with message"""
        game = games.get_by_urlsafe(request.urlsafe_game_key)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')
 
        user = users.get_by_name(request.name)
        if user.key != game.next_move:
            raise endpoints.BadRequestException('It\'s not your turn!')
         
        # Ask the games service to verify move is valid, exception raised if not
        games.is_valid_move(game, request.row, request.column)
        
        # Make the move on the gridboard, change turn of user if necessary
        message = games.make_move(game, request.row, request.column, (user.key == game.first_user))
         
        #if the game is over, assign a winner and loser 
        if game.game_over:
            users.add_win(game.winner.get())
            users.add_loss(game.loser.get()) 
         
        return games.to_form(game, message)
    
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user =  users.get_by_name(request.name)
        if not user:
            raise endpoints.BadRequestException('User not found!')
        user_games = games.get_user_games(user)
        return GameForms(items=[games.to_form(game) for game in user_games])
        