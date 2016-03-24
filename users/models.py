"""
The class definitions for the Datastore entities used in the user service. 
Created on 18/03/2016

@author: thurstonemerson
"""

from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)

#     def win_percentage(self):
#         if self.total_played > 0:
#             return float(self.wins)/float(self.total_played)
#         else:
#             return 0
# 
#     def to_form(self):
#         return UserForm(name=self.name,
#                         email=self.email,
#                         wins=self.wins,
#                         total_played=self.total_played,
#                         win_percentage=self.win_percentage)
# 
#     def add_win(self):
#         """Add a win"""
#         self.wins += 1
#         self.total_played += 1
#         self.put()
# 
#     def add_loss(self):
#         """Add a loss"""
#         self.total_played += 1
#         self.put()


