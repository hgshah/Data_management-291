# MongoDB-DocuStore
MongoDB-DocuStore is a command line program written in Python allowing users to interact with posts stored on a MongoDB database. Allows users to post questions, search for questions, answer a question, list the existing answers, and vote on posts.

## Developers
- Ryan Kortbeek
- Harsh Shah

## Installation
1. Download source (clone repo)

2. Ensure pymongo is installled

`pip install pymongo` | `pip3 install pymongo`

3. Ensure MongoDB is installed (see [here](https://docs.mongodb.com/manual/installation/) for more info)

## Instructions for Use
1. Run a MongoDB server where PORT_NO is the port to connect to and MONGODB_DATA_FOLDER is the path to the respective folder

`mongod --port PORT_NO --dbpath MONGODB_DATA_FOLDER`

2. In a separate terminal instance navigate to the directory containing the source code files for MongoDB-DocuStore

3. Amend the three json files [Posts.json](), [Tags.json](), and [Votes.json]() such that they contain the desired data regarding the posts and their associated tags and votes

4. Create the Posts, Votes, and Tags collections (drops and recreates them if they already exist) within a MongoDB database named 291db and populates them with the data in the Posts.json, Votes.json, and Tags.json files respectively (the json files should be formatted in the form {“posts”: {“row”: [documents]}} for Posts.json and so on for Votes.json and Tags.json)

`python3 phase1.py PORT_NO`

5. Run the program 

`python3 phase2.py PORT_NO`

## System Architecture
*Note that more details can be found regarding all aspects of the classes and methods below through the comments and structure of the source code.*

The main components that comprising our software architecture are: the DBManager class, Phase1, Phase2, the Screens (StartScreen, MainMenuScreen, PostQuestionScreen, SearchForQuestionScreen, SearchResultsScreen, QuestionActionScreen, and AnswerActionScreen).

### DBManager
This class will be handling the interaction between python and the MongoDB database this program is running on. Some of the major functions are:
    - def _try_creating_indexes
- def _get_new_id
- def _assemble_tag_string
- def add_question
- def num_owned_post_and_avg_score
- def get_num_votes

### Phase1
- def get_search_results
- def add_answer
- def check_vote_eligibility - def add_vote
- def get_answers
- def increment_view_count
 This class will be handling the functionality of connecting the program with the MongoDB server at the specified port and creating a database named 291db. It will then read three json files namely Posts.json, Tags.json, and Votes.json and create collections named Posts, Tags, and Votes, respectively, for each - if these collections already exist the existing collections will be dropped and the data from the json files will be entered as documents into newly created collections. Some of the major functionality of this class can be found in:
- def _drop_collections() 
- def _populate_collections()
- def _close()

### Phase2/Driver
This class will act as a driver for the program by initializing a connection to the MongoDB database created in Phase 1 at the specified port via the DBManager class and then passing this DBManager instance to the StartScreen and consequently the MainMenu screen allowing those classes to access the database via the methods of DBManager. It uses the StartScreen class to get a user id (if specified) and then uses the MainMenu class to provide the user with the required functionality. Some of the major functionality of this class can be found in:
- def run()

### BaseScreen
This class serves as an abstract class for all the screens. It also has a couple utility functions that are used by multiple subclasses. Some of the major functionality of this class can be found in:
- def _setup(): must be implemented by all subclasses and is called in the constructor
- def try_adding_votes(): this method tries to add a vote from the specified user to the specified post (the user must be eligible to vote on the post for the vote to be added)
- def run(): this method should be the single access point to the functionality that the screen supports and should run that functionality upon being called - depending on the screen it may or may not return something

### StartScreen(BaseScreen)
This class will provide a chance to a user to choose whether they would like to provide a user id or not. If they choose to provide a user id they are prompted to enter it. Ensures the specified user id is numeric and then uses the DBManager class to create the required user report. Some of the major functionality of this class can be found in:
- def run()

### MainMenu(BaseScreen)
This class represents the main menu screen. If the user has specified a user id a user report will be displayed showing the number of owned questions, average score of owned questions, number of owned answers, average score of owned answers, and number of votes registered to them. Every time the user returns to the main menu the user report is updated to ensure the data is correct. Gives the user the option to post a question, search for questions, or end the program. Some of the major functionality of this class can be found in:
- def _setup() 
- def _refresh()
- def run()

### PostQuestion(BaseScreen)
This class allows the user to post a question that will be added to the Posts collection. Prompts the user to enter the title and body of their question and zero or more tags. If the tags do not already exist in the Tags collection, they will be added. Some of the major functionality of this class can be found in:
- def run(): this allows the user to enter the title and body of the question and zero or more tags then uses the DBManager class to add the question and any new tags (if necessary)

### SearchForQuestion(BaseScreen)
Allows the user to provide one or more keywords to search and passes the space separated keywords as a list to the SearchResults screen where all the questions that contain at least one keyword in either their title, body, or tag field is retrieved.

### SearchResults(BaseScreen)
Retrieves all the questions that contain at least one of the searched keywords in either their title, body, or tag field. Displays all retrieved questions and displays up to 10 at a time. Allows the user to either enter the number corresponding to the question that they would like to perform an action on, see more search results (if possible), or return to the main menu. Some of the major functionality of this class can be found in:
- def _display_search_results() 
- def run()

### QuestionAction(BaseScreen)
Displays all fields of the question that the user has selected to perform an action on, increments the view count of the question, and gives the user a list of actions that they can take based on a number of factors (see below). The actions are as follows:
1. Answer question: allows the user to answer the selected question
2. List existing answers: allows the user view existing answers to the question - these answers are displayed up to
10 at a time. If there is an accepted answer it is displayed first and denoted by stars (i.e. [1]*******************). Allows the user to either enter the number corresponding to the answer that they would like to perform an action on, see more answers (if possible), or return to the main menu.
3. Add a vote: allows the user to add a vote to the selected question (if eligible)
4. Return to the main menu

Some of the major functionality of this class can be found in:
- def _setup()
- def _answer_question()
- def _display_answers()
- def _list_answers() 
- def run()

### AnswerAction (BaseScreen)
Displays all fields of the answer that the user has selected to perform an action on, and gives the user the option to either add a vote to the selected answer (if eligible) or return to the main menu.

## References
 - PyMongo Documentation (https://pymongo.readthedocs.io/en/stable/)
 - MongoDB Documentation (https://docs.mongodb.com/manual/introduction/)
