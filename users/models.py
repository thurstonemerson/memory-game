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
    #win_percentage = ndb.ComputedProperty(lambda self: float(self.wins)/float(self.total_played) if self.total_played > 0 else 0)
     
    @property
    def win_percentage(self):
        if self.total_played > 0:
            return float(self.wins)/float(self.total_played)
        else:
            return 0
