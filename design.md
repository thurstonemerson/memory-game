##Design Decisions

- I added my API endpoints into a package named api, and split the code into a game section
and a user section. I think this makes the api code more easy to read and is a more easily 
extensible design solution, if the game were to become more complicated more api sections
can be included and code that isn't related can be neatly segmented.

- I remodeled my game and user code into separate packages and create service classes to 
interact with the models underlying those pieces of logic. This allowed me to separate concerns
in the code. The api does not contain any game logic at all, instead it calls a game service
which interacts with the game models.

- The service code in each logical package inherits from a (core) service class. This service 
class encapsulates logic used for interacting with the google app engine ndb.model classes.
The inspiration I used for this service/api design came from the flask/sqlalchemy boilerplate
project https://github.com/mattupstate/overholt.

- I am not altogether happy with the way the game logic passes around string messages to be returned
to the user. There is not really a reason for it to be a separate string passed around when
it eventually gets copied to a form object. Ultimately, I think I would change this to be a status 
message situated within a game form. 

- Within the game model, I added firstGuess and secondGuess properties to keep track of where
the user was up to on their turn. It would have also been possible to have used one api call
for both guesses, this would minimise the api calls on the client side.

- I also keep track of each score from each user (first_user_score and second_user_score), so that
when the game is over I can assign a winner. There is also a winner and loser property on the game
model, which will be copied over to the score model.

- I find out whether or not a game has ended by checking the unmatched_pairs properties. 
At the beginning of a game, this property is assigned the number of pairs contained within the
game board.

- I added a complete suite of functional api tests and unit tests for the game and user code.
I found this essential in testing whether additions to the code had broken anything in the game
logic once it started becoming more complicated.

- I added a push task to email the other user when one user has completed their turn.
   