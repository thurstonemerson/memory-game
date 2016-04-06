'''
Created on 6/04/2016

Functional testing module for game api using WebTest library.

@author: thurstonemerson
'''

import webtest
import endpoints

from users.models import User
from api.games import GameApi
from tests import MemoryGameUnitTest


class GameApiTest(MemoryGameUnitTest):
    
    def _get_two_players(self, name_one="good golly", name_two="my mummy"): 
        first_user = User(name=name_one, email=u'generic@thingy.com')
        first_user.put()
        
        second_user = User(name=name_two, email=u'generic@thingy.com')
        second_user.put()  
        
        return (first_user, second_user) 

    def test_endpoint_testApi(self):
        
        #create the api 
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create two players
        first_user, second_user = self._get_two_players() 
      
        #the expected request object as a dictionary
        request = {"first_user":first_user.name, "second_user":second_user.name} 
        
        # To be serialised to JSON by webtest
        resp = testapp.post_json('/_ah/spi/GameApi.new_game', request)
        
        #check correct default values have been created
        self.assertEqual(resp.json['next_move'], first_user.name)
        self.assertEqual(resp.json['game_over'], False)
        self.assertEqual(resp.json['unmatched_pairs'], "8")
        self.assertEqual(resp.json['first_user_score'], "0")
        self.assertEqual(resp.json['second_user_score'], "0")
     


