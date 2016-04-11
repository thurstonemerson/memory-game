'''
Created on 6/04/2016
 
Functional testing module for user api using WebTest library.
 
@author: thurstonemerson
'''
 
import webtest
import endpoints
 
from users.models import User
from api.users import UserApi
from tests import MemoryGameUnitTest
 
 
class UserApiTest(MemoryGameUnitTest):
     
     
    def test_get_user_rankings(self):
        """Test that you are able to retrieve a list of all users ranked by win percentage"""
         
        api_call = '/_ah/spi/UserApi.get_user_rankings'
        app = endpoints.api_server([UserApi], restricted=False)
        testapp = webtest.TestApp(app)
         
        user = User(name=u'no win', email=u'generic@thingy.com')
        user.put()
         
        userone = User(name=u'one win', email=u'generic@thingy.com', total_played=1, wins=1)
        userone.put()
         
        usertwo = User(name=u'two wins', email=u'generic@thingy.com', total_played=2, wins=1)
        usertwo.put()
         
        #the expected request object as a dictionary, to be serialised to JSON by webtest
        resp = testapp.post_json(api_call)
          
        self.assertEqual(len(resp.json['items']), 2)
        self.assertEquals(resp.json['items'][1]['name'], usertwo.name)
        self.assertEquals(resp.json['items'][1]['email'], "generic@thingy.com")
        self.assertEquals(resp.json['items'][1]['wins'], "1")
        self.assertEquals(resp.json['items'][1]['total_played'], "2")
        self.assertEquals(resp.json['items'][1]['win_percentage'], 0.5)
        self.assertEquals(resp.json['items'][0]['name'], userone.name)
        self.assertEquals(resp.json['items'][0]['email'], "generic@thingy.com")
        self.assertEquals(resp.json['items'][0]['wins'], "1")
        self.assertEquals(resp.json['items'][0]['total_played'], "1")
        self.assertEquals(resp.json['items'][0]['win_percentage'], 1)
