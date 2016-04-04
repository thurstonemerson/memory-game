'''
Created on 30/03/2016

Testing module for running unit tests on public methods from the users service.
Uses a sqllite database so that the google app engine doesn't need to be running.

@author: thurstonemerson
'''
from tests import MemoryGameUnitTest

from services import users
from users.models import User

from google.appengine.api import datastore_errors
 

class UserTest(MemoryGameUnitTest):
        
    def test_create(self):
        """Test that a new user can be created"""
        
        name="mytest"
        email="tester@testme.com"
        
        #test user can be created successfully when given correct values
        user = users.create(Request(name, email))    
        self.assertIsInstance(user, User)
        self.assertEquals(user.name, name)
        self.assertEquals(user.email, email)
        
        #ensure that an error is raised when essential attributes are missed
        self.assertRaises(datastore_errors.BadValueError, users.create, None)    

    def test_get_by_name(self):
        """Test that you are able to retrieve a user by name"""
        user = User(name=u'good golly', email=u'generic@thingy.com')
        user.put()
        
        new_user = users.get_by_name(user.name)
        self.assertEquals(user.key, new_user.key)
        self.assertEquals(None, users.get_by_name(""))
        
    def test_get_user_rankings(self):
        """Test that you are able to retrieve a list of all users ranked by win percentage"""
        user = User(name=u'no win', email=u'generic@thingy.com')
        user.put()
        
        userone = User(name=u'one win', email=u'generic@thingy.com', total_played=1, wins=1)
        userone.put()
        
        usertwo = User(name=u'two wins', email=u'generic@thingy.com', total_played=2, wins=1)
        usertwo.put()
        
        user_rankings = users.get_user_rankings()
        self.assertEquals(len(user_rankings), 2)
        self.assertEquals(user_rankings.pop().key, usertwo.key)
        self.assertEquals(user_rankings.pop().key, userone.key)
        
        
class Request():
    """Mocking the google app engine request class"""
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
    def all_fields(self):
        return [Field("name"), Field("email")]
    
class Field():
    """"Mocking an individual field in a request class"""
    def __init__(self, name):
        self.name = name
        