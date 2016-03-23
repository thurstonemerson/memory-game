'''
Created on 21/03/2016

Create the service instances required for interacting with the ndb.model classes

@author: thurstonemerson
'''

from games import GamesService
from users import UsersService


#: An instance of the :class:`GamesService` class
games = GamesService()

#: An instance of the :class:`UsersService` class
users = UsersService()


