'''
User service module, where all the logic of user creation and updating 
is contained. Persistence is dealt with in the service (through super module).

Created on 18/03/2016

@author: thurstonemerson
'''

from models import User
from core import Service
from forms import UserForm
import logging

class UsersService(Service):
    __model__ = User
    
    def get_user_rankings(self):
        "Return a list of users ranked by their win percentage"
        users = super(UsersService, self).find(User.total_played > 0)
        return sorted(users, key=lambda x: x.win_percentage, reverse=True)
    
    def add_win(self, user):
        """Add a win"""
        user.wins += 1
        user.total_played += 1
        super(UsersService, self).save(user)
 
    def add_loss(self, user):
        """Add a loss"""
        user.total_played += 1
        super(UsersService, self).save(user)
        
    def to_form(self, user):
        return UserForm(name=user.name,
                        email=user.email,
                        wins=user.wins,
                        total_played=user.total_played,
                        win_percentage=user.win_percentage)
