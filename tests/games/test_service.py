'''
Created on 30/03/2016

Testing module for running unit tests on public methods from the games service.
Uses a sqllite database so that the google app engine doesn't need to be running.

@author: Jessica
'''
import unittest
import logging
from services import games
from users.models import User
from games.models import CardNames, Card

from google.appengine.ext import ndb
from google.appengine.ext import testbed
 

class GameTest(unittest.TestCase):
    nosegae_datastore_v3 = True
    nosegae_datastore_v3_kwargs = {  
        'datastore_file': 'c:/temp/nosegae.sqlite3',  
        'use_sqlite': True  
    }
    
    def setUp(self):
        """Set up the test bed and activate it"""
        logging.info("Setting up testbed...")
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
        """Create a new game and test all the default information is correct"""
        logging.info("Testing game creation")
        first_user = User(name=u'good golly', email=u'generic@thingy.com')
        first_user.put()
        
        second_user = User(name=u'my mummy', email=u'generic@thingy.com')
        second_user.put()
        
        #create a new game
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
                    
            
    def test_is_valid_move(self):  
        """Test that valid moves are allowed and invalid moves are not"""     
        logging.info("Testing is valid move")
        
    def test_to_form(self):   
        """Test that a game form can be created"""    
        logging.info("Testing to form")
        
    def test_make_move(self):    
        """Test that a move can be made"""   
        logging.info("Testing make a move")
        
        
    def tearDown(self):
        """Tear down the test bed by deactivating it"""
        logging.info("Tearing down testbed...")
        self.testbed.deactivate()