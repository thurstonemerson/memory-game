"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='memory', version='v1')
class MemoryApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        first_user = User.query(User.name == request.first_user).get()
        second_user = User.query(User.name == request.second_user).get()
        if not first_user and second_user:
            raise endpoints.NotFoundException(
                    'One of users with that name does not exist!')

        game = Game.new_game(first_user.key, second_user.key)

        return game.to_form('Good luck playing Memory!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        
        message = "Not implemented"
    
#         if tile.flipped:
#             pass
# 
#         tile.flip();
# 
#         if firstGuess is None or secondGuess is not None:
# 
#             #two unmatching guesses have been made already, start a new guess
#             if secondGuess is not None:
#                 firstGuess.flip();
#                 secondGuess.flip();
#                 firstGuess = secondGuess = None
#             
#             #you have made a first guess, you have one more guess to make
#             firstGuess = tile
#             message = "One more guess to make"
# 
#         else:
# 
#             #If the first guess matches the selected tile, we have a match
#             if firstGuess.title == tile.title:
#                 unmatchedPairs--
#                 message = (this.unmatchedPairs > 0) ? "You made a match" : "You won the game";
#                 firstGuess = secondGuess = None
#             else:
#                 secondGuess = tile
#                 message = "Not a match"
     
        return game.to_form(message)
        
api = endpoints.api_server([MemoryApi])