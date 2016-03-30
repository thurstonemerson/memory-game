'''
Created on 30/03/2016

@author: Jessica
'''
import unittest
from services import games
from users.models import User
from games.models import CardNames, Card

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

class Request:
    def __init__(self, name):
        self.name = name
        
    def all_fields(self):
        return 

class GameTest(unittest.TestCase):
    nosegae_datastore_v3 = True
    nosegae_datastore_v3_kwargs = {  
        'datastore_file': 'c:/temp/nosegae.sqlite3',  
        'use_sqlite': True  
    }
    
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        ndb.get_context().clear_cache()

    def test_new_game(self):
        #games.new_game("", "")
        #request = Request(name="hello")
        first_user = User(name=u'good golly', email=u'generic@thingy.com')
        first_user.put()
        
        second_user = User(name=u'my mummy', email=u'generic@thingy.com')
        second_user.put()
        
        game = games.new_game(first_user.key, second_user.key)
        
        #check that the game details were created with correct default values
        self.assertEqual(game.first_user, first_user.key)
        self.assertEqual(game.second_user, second_user.key)
        self.assertEqual(game.first_user_score, 0)
        self.assertEqual(game.second_user_score, 0)
        self.assertEqual(game.unmatched_pairs, len(CardNames))
        self.assertEqual(game.next_move, first_user.key)
        self.assertFalse(game.game_over)
        self.assertIsNone(game.winner)
        self.assertIsNotNone(game.board)
        
        #check every game piece is a card
        for row in game.board:
            for item in row:
                self.assertIsInstance(item, Card)
                
        #check that there is a pair of every card type in the deck
        for card_name in CardNames:
            num = 0
            
            for row in game.board:
                for item in row:
                    if item.card_name == card_name:
                        num += 1
                        
            self.assertEqual(num, 2, "There must be 2 {0} in the card deck, only contains {1}".format(card_name, num))
                    
            
                    
        
        
        
        
    def tearDown(self):
        self.testbed.deactivate()