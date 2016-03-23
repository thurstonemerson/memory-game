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


