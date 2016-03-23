'''
User service module, where all the logic of user creation and updating 
is contained. Persistence is dealt with in the service (through super module).

Created on 18/03/2016

@author: thurstonemerson
'''

from models import User
from core import Service
import logging

class UsersService(Service):
    __model__ = User