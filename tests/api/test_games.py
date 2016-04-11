'''
Created on 6/04/2016

Functional testing module for game api using WebTest library.

@author: thurstonemerson
'''

import webtest
import endpoints

from datetime import date
from users.models import User
from games.models import Card, CardNames, Score
from services import games, scores
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
    
    def _get_new_game_with_mock_gridboard(self):
        (game, first_user, second_user) = self._get_new_game()  
        gridboard = [[Card(card_name=CardNames.DEATH), Card(card_name=CardNames.FOOL), Card(card_name=CardNames.DEATH), Card(card_name=CardNames.HIGH_PRIESTESS)],
                     [Card(card_name=CardNames.HANGED_MAN), Card(card_name=CardNames.TEMPERANCE), Card(card_name=CardNames.HIGH_PRIESTESS), Card(card_name=CardNames.LOVERS)],
                     [Card(card_name=CardNames.JUSTICE), Card(card_name=CardNames.FOOL), Card(card_name=CardNames.HERMIT), Card(card_name=CardNames.LOVERS)],
                     [Card(card_name=CardNames.JUSTICE), Card(card_name=CardNames.HANGED_MAN), Card(card_name=CardNames.TEMPERANCE), Card(card_name=CardNames.HERMIT)]]
        game.board = gridboard
        game.put()
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
        request = {"first_user":"", "second_user":""} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
        
        #test calling new game with the same user twice
        request = {"first_user":first_user.name, "second_user":first_user.name} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
        
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
        
        
    def test_make_move_no_match(self):
        """Functional test for api call to make a move"""
        #create the api 
        api_call = '/_ah/spi/GameApi.make_move'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create a new game with a mock gridboard
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
          
        #make the first move, flip DEATH. Test first guess made.  
        #the expected request object as a dictionary, to be serialised to JSON by webtest
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":0} 
        resp = testapp.post_json(api_call, request)
        self.assertEqual(resp.json['message'], "One more guess to make")
          
        #test card is flipped
        self.assertTrue(game.board[0][0].flipped)
        
        #make the second move, flip FOOL. Test match wasn't made.
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":1} 
        resp = testapp.post_json(api_call, request)
        self.assertEqual(resp.json['message'], "Not a match")  
        self.assertTrue(game.board[0][1].flipped)
        
        
    def test_make_move_game_not_found(self):
        """Functional test for api call to make a move"""
        #create the api 
        api_call = '/_ah/spi/GameApi.make_move'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create a new game with a mock gridboard
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
      
        #test not your turn
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":0, "column":1} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
        
        #test game not found
        request = {"urlsafe_game_key":"asadfdsf", "name":first_user.name,  "row":0, "column":1} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
       
        
    def test_make_move_game_already_over(self):
        """Functional test for api call to make a move"""
        #create the api 
        api_call = '/_ah/spi/GameApi.make_move'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create a new game with a mock gridboard
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
    
        game.game_over = True
        game.put()
        
        #test game already over
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":1} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
       
        
    def test_make_move_invalid_move(self):
        """Functional test for api call to make a move"""
        #create the api 
        api_call = '/_ah/spi/GameApi.make_move'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create a new game with a mock gridboard
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
       
        #test exception raised if exceed gridboard boundary
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":-1} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":4, "column":0} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
       
        game.board[0][0].flip()
       
        #test exception raised if card already flipped
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":0} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
       
       
    def test_make_move_winner_loser_score(self):
        """Functional test for api call to make a move"""
        #create the api 
        api_call = '/_ah/spi/GameApi.make_move'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
     
        #create a new game with a mock gridboard
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
         
        #DEATH
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":0} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":2} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)
            
        #FOOL
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":1} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":2, "column":1} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)
          
        #HIGH_PRIESTESS
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":3} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":1, "column":2} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over) 
          
        #HANGED_MAN
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":1, "column":0} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":3, "column":1} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over) 
          
        #TEMPERANCE
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":1, "column":1} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":3, "column":2} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)   
          
        #LOVERS
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":1, "column":3} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":2, "column":3} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)   
          
        #JUSTICE
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":2, "column":0} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":3, "column":0} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)
          
        #HERMIT
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":3, "column":3} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":2, "column":2} 
        testapp.post_json(api_call, request)
          
        #test game is ended when all pairs are found
        self.assertTrue(game.game_over)  
         
        #test correct winner and loser are assigned
        self.assertEqual(game.winner, first_user.key)
        self.assertEqual(game.loser, second_user.key)
          
        #test a score is added to the scoreboard
        score = Score.query(Score.winner == first_user.key).get()
        self.assertEqual(score.winner, first_user.key)
        self.assertEqual(score.loser, second_user.key)
        self.assertEqual(score.winner_score, game.first_user_score)
        self.assertEqual(score.loser_score, game.second_user_score)
        self.assertEqual(score.date, date.today())
        
        
    def test_make_move_draw(self):
        """Functional test for api call to make a move"""
        #create the api 
        api_call = '/_ah/spi/GameApi.make_move'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create a new game with a mock gridboard
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
        
        #DEATH
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":0} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":2} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)
          
        #FOOL
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":1} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":2, "column":1} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)
        
        #HIGH_PRIESTESS
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":0, "column":3} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":1, "column":2} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over) 
        
        #HANGED_MAN
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":1, "column":0} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":first_user.name,  "row":3, "column":1} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over) 
        
        game.next_move = second_user.key
        game.put()
        
        #TEMPERANCE
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":1, "column":1} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":3, "column":2} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)   
        
        #LOVERS
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":1, "column":3} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":2, "column":3} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)   
        
        #JUSTICE
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":2, "column":0} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":3, "column":0} 
        testapp.post_json(api_call, request)
        self.assertFalse(game.game_over)
        
        #HERMIT, test an exception is thrown stating game is a draw
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":3, "column":3} 
        testapp.post_json(api_call, request)
        request = {"urlsafe_game_key":game.key.urlsafe(), "name":second_user.name,  "row":2, "column":2} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
    
    def test_get_user_scores(self):
        """Functional test for api call to retrieve user scores"""
        #create the api 
        api_call = '/_ah/spi/GameApi.get_user_scores'
        app = endpoints.api_server([GameApi], restricted=False)
        testapp = webtest.TestApp(app)
        
        #create some scores
        player_one, player_two = self._get_two_players()
        scores.new_score(winner=player_one.key, loser=player_two.key, first_user_score=3, second_user_score=2)
        
        #test user not found
        request = {"name":"asdfsdf"} 
        self.assertRaises(Exception, testapp.post_json, api_call, request)
       
        #test scores retrieved
        request = {"name":player_one.name} 
        resp = testapp.post_json(api_call, request)
        
        self.assertEqual(len(resp.json['items']), 1)
        self.assertEquals(resp.json['items'][0]['winner'], player_one.name)
        self.assertEquals(resp.json['items'][0]['winner_score'], "3")
        self.assertEquals(resp.json['items'][0]['loser'], player_two.name)
        self.assertEquals(resp.json['items'][0]['loser_score'], "2")
        
        request = {"name":player_two.name} 
        resp = testapp.post_json(api_call, request)
        
        self.assertEqual(len(resp.json['items']), 1)
        self.assertEquals(resp.json['items'][0]['winner'], player_one.name)
        self.assertEquals(resp.json['items'][0]['winner_score'], "3")
        self.assertEquals(resp.json['items'][0]['loser'], player_two.name)
        self.assertEquals(resp.json['items'][0]['loser_score'], "2")
      
