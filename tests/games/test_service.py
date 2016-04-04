'''
Created on 30/03/2016

Testing module for running unit tests on public methods from the games service.
Uses a sqllite database so that the google app engine doesn't need to be running.

@author: thurstonemerson
'''
from tests import MemoryGameUnitTest

from services import games, scores
from users.models import User
from games.models import CardNames, Card

import endpoints
 

class GameTest(MemoryGameUnitTest):
        
        
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
        self.assertIsNone(game.loser)
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
                    
    def test_get_by_urlsafe(self):  
        """Testing retrieval of game by name and urlsafemode"""     
        (game, first_user, second_user) = self._get_new_game()       
              
        #test get model by urlsafe key
        self.assertEqual(games.get_by_urlsafe(game.key.urlsafe()).key, game.key) 
        self.assertRaises(endpoints.BadRequestException, games.get_by_urlsafe, "")
        self.assertRaises(ValueError, games.get_by_urlsafe, first_user.key.urlsafe())           
            
    def test_get_user_games(self):
        """Test that active games of a user can be retrieved""" 
        (game_one, first_user, second_user) = self._get_new_game("first user", "second user") 
        game_one.game_over = True
        game_one.put()
        
        #zero games returned because the user has no active games
        self.assertEqual(len(games.get_user_games(first_user)), 0)
        
        #add an active game
        games.new_game(first_user.key, second_user.key)
        
        #one game returned
        self.assertEqual(len(games.get_user_games(first_user)), 1)
        
    def test_delete_game(self):
        """Test that games are able to be deleted via the games service"""
        (game, first_user, second_user) = self._get_new_game()
           
        try:
            games.delete(game)
        except Exception:
            self.fail("Delete game failed unexpectedly")
          
        
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
        
    
    def test_make_move_game_ended(self): 
        """Test that a game is ended when all pairs are found"""  
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
        
        games.make_move(game, 0, 0, True) #DEATH
        games.make_move(game, 0, 2, True)
        self.assertFalse(game.game_over)  
         
        games.make_move(game, 0, 1, True) #FOOL
        games.make_move(game, 2, 1, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 0, 3, True) #HIGH_PRIESTESS
        games.make_move(game, 1, 2, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 1, 0, True) #HANGED_MAN
        games.make_move(game, 3, 1, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 1, 1, True) #TEMPERANCE
        games.make_move(game, 3, 2, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 1, 3, True) #LOVERS
        games.make_move(game, 2, 3, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 2, 0, True) #JUSTICE
        games.make_move(game, 3, 0, True)
        
        games.make_move(game, 3, 3, True) #HERMIT
        games.make_move(game, 2, 2, True)
        
        #test game is ended when all pairs are found
        self.assertTrue(game.game_over)  
       
        #test correct winner is assigned
        self.assertEqual(game.winner, first_user.key)
        self.assertEqual(game.loser, second_user.key)
        
    def test_draw(self): 
        """Test that a draw results in no winner being assigned"""  
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
        
        games.make_move(game, 0, 0, True) #DEATH
        games.make_move(game, 0, 2, True)
        self.assertFalse(game.game_over)  
         
        games.make_move(game, 0, 1, True) #FOOL
        games.make_move(game, 2, 1, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 0, 3, True) #HIGH_PRIESTESS
        games.make_move(game, 1, 2, True)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 1, 0, True) #HANGED_MAN
        games.make_move(game, 3, 1, True)
        self.assertFalse(game.game_over)  
        
        game.next_move = second_user.key
        
        games.make_move(game, 1, 1, False) #TEMPERANCE
        games.make_move(game, 3, 2, False)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 1, 3, False) #LOVERS
        games.make_move(game, 2, 3, False)
        self.assertFalse(game.game_over)  
        
        games.make_move(game, 2, 0, False) #JUSTICE
        games.make_move(game, 3, 0, False)
        
        games.make_move(game, 3, 3, False) #HERMIT
        games.make_move(game, 2, 2, False)
        
        #test game is ended when all pairs are found
        self.assertTrue(game.game_over)  
       
        #test no winner or loser is assigned
        self.assertIsNone(game.winner)
        self.assertIsNone(game.loser)
        
        
    def test_make_move_match_made(self):    
        """Test that a move can be played where the cards match"""  
        
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
        unmatched_pairs_temp = game.unmatched_pairs
          
        #make the first move, flip DEATH. Test first guess made.  
        message = games.make_move(game, 0, 0, True)
        self.assertEqual(message, "One more guess to make")  
        
        #test card is flipped
        self.assertTrue(game.board[0][0].flipped)
        
        #make the second move, flip DEATH. Test match was made.
        message = games.make_move(game, 0, 2, True)  
        self.assertEqual(message, "You made a match")  
        self.assertTrue(game.board[0][2].flipped)
        
        #test turn is not rotated when a match is made
        self.assertEqual(game.next_move, first_user.key)
        
        #test unmatched pairs is decremented
        self.assertEqual(game.unmatched_pairs, (unmatched_pairs_temp-1))
        
        #after a match is made test the cards are still flipped 
        #after the next turn. 
        message = games.make_move(game, 0, 3, True)  
        self.assertTrue(game.board[0][0].flipped)
        self.assertTrue(game.board[0][2].flipped)
        
        #test first user score is incremented and second user score is not
        self.assertEqual(game.first_user_score, 1)
        self.assertEqual(game.second_user_score, 0)
        
        
    def test_make_move_match_not_made(self):    
        """Test that a move can be played where the cards don't match""" 
        (game, first_user, second_user) = self._get_new_game_with_mock_gridboard()
        unmatched_pairs_temp = game.unmatched_pairs
          
        #make the first move, flip DEATH. Test first guess made.  
        message = games.make_move(game, 0, 0, True)
        self.assertEqual(message, "One more guess to make")  
          
        #test card is flipped
        self.assertTrue(game.board[0][0].flipped)
        
        #make the second move, flip FOOL. Test match wasn't made.
        message = games.make_move(game, 0, 1, True)  
        self.assertEqual(message, "Not a match")  
        self.assertTrue(game.board[0][1].flipped)
        
        #test turn is rotated when a match isn't made
        self.assertEqual(game.next_move, second_user.key)
        
        #test unmatched pairs is not decremented
        self.assertEqual(game.unmatched_pairs, unmatched_pairs_temp)
        
        #after a match is not made test the cards have been flipped 
        #back after the next turn. 
        message = games.make_move(game, 0, 3, False)  
        self.assertFalse(game.board[0][0].flipped)
        self.assertFalse(game.board[0][1].flipped)
        
    def create_score_service(self):    
        
        player_one, player_two = self._get_two_players()
        
        self.assertRaises(endpoints.BadRequestException, scores.create_new, player_one, player_two, 0, 0)
        
        score = scores.create_new(winner=player_one, loser=player_two, first_player_score=3, second_player_score=2)
        self.assertEquals(score.winner, player_one)
        self.assertEquals(score.winner_score, 3)
        self.assertEquals(score.loser, player_two)
        self.assertEquals(score.loser_score, 2)
        