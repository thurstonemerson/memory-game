#Memory Game API for Google App Engine

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
    informed and the next turn will be the other user. 
    If a match is made and this causes a game to end, a corresponding Score entity will be created,
    unless the game is tied, in which case the game will be deleted.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.