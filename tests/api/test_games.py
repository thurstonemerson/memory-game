'''
Created on 6/04/2016

Functional testing module for game api using WebTest library.

@author: thurstonemerson
'''

import webtest
import endpoints

from users.models import User
from services import games
from api.games import GameApi
from tests import MemoryGameUnitTest


class GameApiTest(MemoryGameUnitTest):
    
    def _get_two_players(self, name_one="good golly", name_two="my mummy"): 
        first_user = User(name=name_one, email=u'generic@thingy.com')
        first_user.put()
        
        second_user = User(name=name_two, email=u'generic@thingy.com')
        second_user.put()  
        
        return (first_user, second_user)
    
    def _get_new_game(self, name_one="good golly", name_two="my mummy"):
        """Create a brand new game and return it"""
        first_user, second_user = self._get_two_players(name_one, name_two)
        
        #create a new game
        game = games.new_game(first_user.key, second_user.key)
        return (game, first_user, second_user) 

    def test_new_game(self):
        """Functional test for api call to get a new game"""
        #create the api 
        api_call = '/_ah/spi/GameApi.new_game'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create two players
        first_user, second_user = self._get_two_players() 
      
        #the expected request object as a dictionary, to be serialised to JSON by webtest
        request = {"first_user":first_user.name, "second_user":second_user.name} 
        resp = testapp.post_json(api_call, request)
        
        #check correct default values have been created
        self.assertEqual(resp.json['next_move'], first_user.name)
        self.assertEqual(resp.json['game_over'], False)
        self.assertEqual(resp.json['unmatched_pairs'], "8")
        self.assertEqual(resp.json['first_user_score'], "0")
        self.assertEqual(resp.json['second_user_score'], "0")
        
        #test user not found
        #request = {"first_user":"", "second_user":""} 
        #self.assertRaises(endpoints.NotFoundException, testapp.post_json, api_call, request)
        
        #test calling new game with the same user twice
        #request = {"first_user":first_user.name, "second_user":first_user.name} 
        #self.assertRaises(endpoints.NotFoundException, testapp.post_json, api_call, request)
        
        
        
    def test_get_game(self):
        """Functional test for api call to get an existing game"""
        #create the api 
        api_call = '/_ah/spi/GameApi.get_game'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create two players
        game, first_user, second_user = self._get_new_game() 
      
        #the expected request object as a dictionary, to be serialised to JSON by webtest
        request = {"urlsafe_game_key":game.key.urlsafe()} 
        resp = testapp.post_json(api_call, request)
        
        #check correct default values have been created
        self.assertEqual(resp.json['next_move'], first_user.name)
        self.assertEqual(resp.json['game_over'], False)
        self.assertEqual(resp.json['unmatched_pairs'], "8")
        self.assertEqual(resp.json['first_user_score'], "0")
        self.assertEqual(resp.json['second_user_score'], "0")
     


