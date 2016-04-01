'''
Created on 30/03/2016

Testing module for running unit tests on public methods from the users service.
Uses a sqllite database so that the google app engine doesn't need to be running.

@author: thurstonemerson
'''
import unittest

from services import users
from users.models import User

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import datastore_errors
 

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

class UserTest(unittest.TestCase):
    nosegae_datastore_v3 = True
    nosegae_datastore_v3_kwargs = {  
        'datastore_file': 'c:/temp/nosegae.sqlite3',  
        'use_sqlite': True  
    }
       
    
    def setUp(self):
        """Set up the test bed and activate it"""
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        ndb.get_context().clear_cache()
        

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
        """Create a new game and test all the default information is correct"""
        
    def tearDown(self):
        """Tear down the test bed by deactivating it"""
        self.testbed.deactivate()
        
        
        