# MongoDB-DocuStore

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



## References
 - PyMongo Documentation (https://pymongo.readthedocs.io/en/stable/)
 - MongoDB Documentation (https://docs.mongodb.com/manual/introduction/)
