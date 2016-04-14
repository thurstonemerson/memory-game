#Memory Game API for Google App Engine

API explorer for deployed game can be found here: http://my-memory-game.appspot.com/_ah/api/explorer

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
##Testing:

A suite of functional API tests and unit tests are included in the source. To run them, alter the
SDK_PATH in the config.py file and insert the path to the google app engine sdk. Tests
can be launched with the following command:

	python test_runner.py
 
 
##Game Description:

Which player has the better memory? In this simple 2 player game of memory beloved by children the world round,
you flip two cards and remember the pictures on them. If you don't get a match then it is the next player's turn.
If you get a match, then you can flip two more cards! Whoever collects more pairs is the winner. 

Each board contains a pair of cards from the 8 possible card types:
DEATH,TEMPERANCE,HIGH_PRIESTESS,HERMIT,HANGED_MAN,LOVERS,JUSTICE,FOOL

The board is represented as a 2D list of cards with XXX indicating an unflipped
card and the card name indicating a flipped card:
[[XXX, XXX, XXX, XXX], 
[XXX, HANGED_MAN, XXX, XXX], 
[XXX, XXX, XXX, XXX], 
[XXX, XXX, XXX, HERMIT]

For API testing purposes, a board may be represented as a 2D list of cards and
a boolean value indicating whether or not the card has been flipped:
[[FOOL:False, TEMPERANCE:False, LOVERS:False, HANGED_MAN:False], 
[TEMPERANCE:False, HANGED_MAN:False, JUSTICE:False, DEATH:False], 
[HERMIT:False, DEATH:False, JUSTICE:False, HIGH_PRIESTESS:False], 
[FOOL:False, HIGH_PRIESTESS:False, LOVERS:False, HERMIT:False]]

To see the 2D list of cards with boolean value, change the DEBUG setting in the
config.py file to True.

To make a move, row and column values must be represented in array index values,
ie each index begins at 0 not 1.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **get_user_rankings**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Rank all players that have played at least one game by their
    winning percentage and return.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: first_user, second_user
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. `first_user` and `second_user` are the names of the
    of the two players, first_user will be the first player to take a turn in the game.
    Will raise a NotFoundException if either user does not exist. Will raise a BadRequestException
    if the player names are the same.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Will raise a NotFoundException if game does not exist.
    Returns the current state of a game. 
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, user_name, row, column
    - Returns: GameForm with new game state.
    - Description: Will raise a NotFoundException if game does not exist.
    Will raise a BadRequestException if game is already over.
    Will raise a BadRequestException if the wrong user attempts to take a turn.
    Will raise a BadRequestException if a move attempted to moved outside the gridboard 
    or flips an already flipped card.
    Accepts a move and returns the updated state of the game.
    Row and column represent a request to flip a card on the game board at indexes between 0 and 3.
    For a users first guess, the card is flipped and a message is returned informing the user
    they have one more guess to make. For a users second guess, if a match is made the user is
    informed and the user's game score is incremented by one. If a match is not made, the user is
    informed and the next turn will be the other user - an email is sent to notify the other user it is 
    their turn. If a match is made and this causes a game to end, a corresponding Score entity will be created,
    unless the game is tied, in which case the game will be deleted.
    
    
 - **get_user_scores**
    - Path: 'scores/user/{name}'
    - Method: GET
    - Parameters: name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: name
    - Returns: ScoreForms. 
    - Description: Returns all active games recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
  - **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: StringMessage confirming deletion
    - Description: Deletes the game. If the game is already completed a BadRequestException
    will be thrown. Will raise a NotFoundException if the game does not exist.
    
  - **get_game_history**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: StringMessage containing history
    - Description: Returns the move history of a game as a stringified list in the form 
    [user, first_guess, second_guess, match_made] where each guess is represented by a
    card name, row number, and columne number:
    eg. [patrick:FOOL:0:0:HANGED_MAN:1:0:False, timothy:JUSTICE:2:0:LOVERS:2:2:False]

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    - Also keeps track of wins and total_played.
    
 - **Game**
    - Stores unique game states. Associated with User models via KeyProperties
    first_user and second_user.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty as
    well.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, board,
    user_x, user_o, game_over, winner, next_move, unmatched_pairs, first_user_score, 
    second_user_score, history).   
 - **NewGameForm**
    - Used to create a new game (first_user, second_user)
 - **MakeMoveForm**
    - Inbound make move form (name, row, column).
 - **ScoreForm**
    - Representation of a completed game's Score (date, winner, loser, winner_score, loser_score).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserForm**
    - Representation of User. Includes winning percentage
 - **UserForms**
    - Container for one or more UserForm.
 - **StringMessage**
    - General purpose String container.
    