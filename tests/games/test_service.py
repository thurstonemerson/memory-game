'''
Created on 30/03/2016

Testing module for running unit tests on public methods from the games service.
Uses a sqllite database so that the google app engine doesn't need to be running.

@author: Jessica
'''
import unittest
import endpoints

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
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        ndb.get_context().clear_cache()
        
    def _get_new_game(self):
        """Create a brand new game and return it"""
        first_user = User(name=u'good golly', email=u'generic@thingy.com')
        first_user.put()
        
        second_user = User(name=u'my mummy', email=u'generic@thingy.com')
        second_user.put()
        
        #create a new game
        game = games.new_game(first_user.key, second_user.key)
        return (game, first_user, second_user)
        

    def test_new_game(self):
        """Create a new game and test all the default information is correct"""

        (game, first_user, second_user) = self._get_new_game()
        
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
                    
    def test_get_by_name_and_urlsafe(self):  
        """Testing retrieval of game by name and urlsafemode"""     
        #(game, first_user, second_user) = self._get_new_game()       
                
        #games.get_by_urlsafe(game.) 
        
        #test invalid model
        #games.get_by_name(model_name)    
            
            
    def test_is_valid_move(self):  
        """Test that valid moves are allowed and invalid moves are not"""  
        (game, first_user, second_user) = self._get_new_game()
        
        #test that a move outside of the gridboard boundary throws an exception
        self.assertRaises(endpoints.BadRequestException, games.is_valid_move, game, 4, 0)
        self.assertRaises(endpoints.BadRequestException, games.is_valid_move, game, 0, 4)
        self.assertRaises(endpoints.BadRequestException, games.is_valid_move, game, -1, 0)
        self.assertRaises(endpoints.BadRequestException, games.is_valid_move, game, 0, -1)
           
        #test that move where card is already flipped is invalid
        game.board[3][3].flip()
        game.put()
        self.assertRaises(endpoints.BadRequestException, games.is_valid_move, game, 3, 3)
        
        #test that a move in the gridboard boundary where card isn't flipped is valid
        self.assertTrue(games.is_valid_move(game, 0, 0))
        
        #test that it doesn't throw an exception if asked
        try:
            games.is_valid_move(game, 4, 0, False)
            games.is_valid_move(game, 3, 3, False)
            games.is_valid_move(game, 0, 0, False)
        except endpoints.BadRequestException:
            self.fail("is_valid_move raised BadRequestException unexpectedly")
            
        #test that false is returned when move is invalid or card is flipped
        self.assertFalse(games.is_valid_move(game, 4, 0, False))
        self.assertFalse(games.is_valid_move(game, 3, 3, False))
        
    def test_to_form(self):   
        """Test that a game form can be created"""
        message = "This is a message"
        (game, first_user, second_user) = self._get_new_game()
        game_form = games.to_form(game, message)
        
        self.assertEqual(game.key.urlsafe(), game_form.urlsafe_key)
        self.assertEqual(str(game.board), game_form.board)
        self.assertEqual(first_user.name, game_form.next_move)
        self.assertFalse(game_form.game_over)
        self.assertEqual(game.unmatched_pairs, game_form.unmatched_pairs)
        self.assertEqual(game.first_user_score, game_form.first_user_score)
        self.assertEqual(game.second_user_score, game_form.second_user_score)
        self.assertEqual(message, game_form.message)
        self.assertEqual(game.winner, game_form.winner)
        
        #test winner if true
        game.winner = first_user.key
        game.put()
        game_form = games.to_form(game, message)
        self.assertEqual(first_user.name, game_form.winner)
        
        #test next move
        game.next_move = second_user.key
        game.put()
        game_form = games.to_form(game, message)
        self.assertEqual(second_user.name, game_form.next_move)
        
        
        
    def test_make_move(self):    
        """Test that a move can be made"""   
        
        
    def tearDown(self):
        """Tear down the test bed by deactivating it"""
        self.testbed.deactivate()