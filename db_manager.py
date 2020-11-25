from pymongo import MongoClient, collation, ASCENDING, DESCENDING, TEXT
from datetime import datetime
import re

DB_NAME = '291db'
SEARCH_INDEX = 'search_index'
QUESTION_TYPE_ID = '1'
ANSWER_TYPE_ID = '2'


class DBManager:
    """
    Class handling the interaction between python and MongoDB.
    """

    def __init__(self, port):
        """
        Gets a MongoDB client that is connected to the MongoDB server at the specified port. Gets a pymongo database
        with name DB_NAME and collections named Posts, Tags, and Votes. Creates indexes for queries that are commonly
        used in order to optimize the performance of this program.
        :param port: int corresponding to the port to connect to the MongoDB server at
        """
        self.client = MongoClient(port=port)
        self.db = self.client[DB_NAME]
        self.tag_Id_index = 'tag_Id_index'
        self.question_search_index = 'question_search_index'
        self.find_answers_index = 'find_answers_index'
        self.posttypeid_index = 'post_type_id_index'
        self.post_Id_index = 'post_Id_index'
        self.post_owner_index = 'post_owner_index'
        self.vote_Id_index = 'vote_Id_index'
        self.vote_userid_index = 'vote_user_id_index'
        self.vote_postid_userid_index = 'vote_postid_userid_index'
        self.posts, self.tags, self.votes = self.db['Posts'], self.db['Tags'], self.db['Votes']
        self._try_creating_indexes()

    def _try_creating_indexes(self):
        """
        Tries to create indexes (if they have not already been created) that optimize the performance of this
        application.
        """
        post_indexes = self.posts.list_indexes()
        tag_indexes = self.tags.list_indexes()
        vote_indexes = self.votes.list_indexes()
        print('Creating indexes...')
        if self.question_search_index not in post_indexes:
            self.posts.create_index(
                [('Tags', TEXT), ('Title', TEXT), ('Body', TEXT)],
                name=self.question_search_index
            )
        if self.find_answers_index not in post_indexes:
            self.posts.create_index(
                [('PostTypeId', ASCENDING), ('ParentId', ASCENDING)],
                name=self.find_answers_index
            )
        if self.posttypeid_index not in post_indexes:
            self.posts.create_index(
                [('PostTypeId', ASCENDING)],
                name=self.posttypeid_index
            )
        if self.post_Id_index not in post_indexes:
            self.posts.create_index(
                [('Id', ASCENDING)],
                collation=collation.Collation('en_US', numericOrdering=True),
                name=self.post_Id_index
            )
        if self.post_owner_index not in post_indexes:
            self.posts.create_index(
                [('PostTypeId', ASCENDING), ('OwnerUserId', ASCENDING)],
                name=self.post_owner_index
            )
        if self.tag_Id_index not in tag_indexes:
            self.tags.create_index(
                [('Id', ASCENDING)],
                collation=collation.Collation('en_US', numericOrdering=True),
                name=self.tag_Id_index
            )
        if self.vote_Id_index not in vote_indexes:
            self.votes.create_index(
                [('Id', ASCENDING)],
                collation=collation.Collation('en_US', numericOrdering=True),
                name=self.vote_Id_index
            )
        if self.vote_userid_index not in vote_indexes:
            self.votes.create_index(
                [('UserId', ASCENDING)],
                name=self.vote_userid_index
            )
        if self.vote_postid_userid_index not in vote_indexes:
            self.votes.create_index(
                [('PostId', ASCENDING), ('UserId', ASCENDING)],
                name=self.vote_postid_userid_index
            )

    def _get_new_id(self, id_type):
        """
        Gets a new unique Id value either the Posts, Votes, or Tags collection as specified by id_type. This is done
        by finding the current max Id value in the respective collection and then incrementing that by 1 and returning
        the new value as a string.
        :param id_type: string that corresponds to the collection to get a new unique Id value for (one of 'post',
                        'vote', or 'tag')
        :return: a new unique Id value for the specified table
        """
        res = {}
        max_id_query = [('Id', DESCENDING)]
        if id_type == 'post':
            res = self.posts.find_one(
                sort=max_id_query,
                collation=collation.Collation('en_US', numericOrdering=True)
            )
        elif id_type == 'vote':
            res = self.votes.find_one(
                sort=max_id_query,
                collation=collation.Collation('en_US', numericOrdering=True)
            )
        elif id_type == 'tag':
            res = self.tags.find_one(
                sort=max_id_query,
                collation=collation.Collation('en_US', numericOrdering=True)
            )
        return str(int(res['Id']) + 1)

    def _assemble_tag_string(self, tags):
        """
        Assembles a tag string by wrapping each tag with '<' and '>'. If any of the tags do not exist in the Tags
        collection they are added and for the tags that already exist their Count value is incremented.
        :param tags: list containing the tags
        :return: tag string containing each tag wrapped with '<' and '>'
        """
        if len(tags) == 0:
            return None
        tag_string = ''
        for tag in tags:
            if tag.lower() not in tag_string:
                tag_string += '<' + tag.lower() + '>'
                res = self.tags.find_one({'TagName': tag.lower()})
                if res is None:
                    write_res = self.tags.insert_one({'Id': self._get_new_id('tag'), 'TagName': tag.lower(), 'Count': 1})
                else:
                    self.tags.update_one({'_id': res['_id']}, {'$inc': {'Count': 1}})
        return tag_string

    def get_num_owned_posts_and_avg_score(self, user_id, post_type):
        """
        Gets the number of owned posts of a certain type (either question - PostTypeId of 1, or answer - PostTypeId of
        2) and the average score of those posts.
        :param user_id: int corresponding to the OwnerUserId to look for
        :param post_type: int corresponding to the post type (1 if post type is question and 2 if post type is answer)
        :return: tuple of int, float where the int corresponds to the number of owned posts and the float corresponds
                 to the average score of those posts.
        """
        owned_posts_pipeline = [
            {'$match': {'$and': [{'PostTypeId': str(post_type)}, {'OwnerUserId': str(user_id)}]}},
            {'$count': 'num_posts'}
        ]
        res1 = list(self.posts.aggregate(owned_posts_pipeline))
        num_post_type = 0 if len(res1) != 1 else res1[0]['num_posts']
        avg_score_pipeline = [
            {'$match': {'$and': [{'PostTypeId': str(post_type)}, {'OwnerUserId': str(user_id)}]}},
            {'$group': {'_id': {'user_id': '$OwnerUserId'}, 'avg_score': {'$avg': '$Score'}}}
        ]
        res2 = list(self.posts.aggregate(avg_score_pipeline))
        post_type_avg_score = 0 if len(res2) != 1 else res2[0]['avg_score']
        return num_post_type, post_type_avg_score

    def get_num_votes(self, user_id):
        """
        Gets the number of votes registered by a user.
        :param user_id: int corresponding to the UserId to look for
        :return: an int corresponding to the number of votes registered by the user
        """
        num_votes_pipeline = [
            {'$match': {'UserId': str(user_id)}},
            {'$count': 'num_votes'}
        ]
        res2 = list(self.votes.aggregate(num_votes_pipeline))
        return 0 if len(res2) != 1 else res2[0]['num_votes']

    def add_question(self, title, body, tags, user_id, content_license='CC BY-SA 2.5'):
        """
        Adds a question post to the Posts collection.
        :param title: question title
        :param body: question body
        :param tags: list containing the question tags
        :param user_id: id of user who is posting the answer (if None the question post that is added to the Posts
                        collection will not have a OwnerUserId field - likewise in the case that the tags list is empty)
        :param content_license: 'CC BY-SA 2.5' by default
        """
        tag_string = self._assemble_tag_string(tags)
        if user_id is not None:
            if tag_string is None:
                insertion = {
                    'Id': self._get_new_id('post'),
                    'PostTypeId': QUESTION_TYPE_ID,
                    'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3],
                    'Score': 0,
                    'ViewCount': 0,
                    'Body': body,
                    'OwnerUserId': str(user_id),
                    'Title': title,
                    'AnswerCount': 0,
                    'CommentCount': 0,
                    'FavoriteCount': 0,
                    'ContentLicense': content_license
                }
            else:
                insertion = {
                    'Id': self._get_new_id('post'),
                    'PostTypeId': QUESTION_TYPE_ID,
                    'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3],
                    'Score': 0,
                    'ViewCount': 0,
                    'Body': body,
                    'OwnerUserId': str(user_id),
                    'Title': title,
                    'Tags': tag_string,
                    'AnswerCount': 0,
                    'CommentCount': 0,
                    'FavoriteCount': 0,
                    'ContentLicense': content_license
                }
        else:
            if tag_string is None:
                insertion = {
                    'Id': self._get_new_id('post'),
                    'PostTypeId': QUESTION_TYPE_ID,
                    'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3],
                    'Score': 0,
                    'ViewCount': 0,
                    'Body': body,
                    'Title': title,
                    'AnswerCount': 0,
                    'CommentCount': 0,
                    'FavoriteCount': 0,
                    'ContentLicense': content_license
                }
            else:
                insertion = {
                    'Id': self._get_new_id('post'),
                    'PostTypeId': QUESTION_TYPE_ID,
                    'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3],
                    'Score': 0,
                    'ViewCount': 0,
                    'Body': body,
                    'Title': title,
                    'Tags': tag_string,
                    'AnswerCount': 0,
                    'CommentCount': 0,
                    'FavoriteCount': 0,
                    'ContentLicense': content_license
                }
        write_res = self.posts.insert_one(insertion)

    def get_search_results(self, keywords):
        """
        Gets the questions from the Posts collection that contain at least one of the searched keywords in either their
        title, body, or tag fields. Our implementation finds case-insensitive and partial matches. Uses regex to find
        the matching questions.
        :param keywords: space separated string of keywords
        :return: list of dicts corresponding to the documents of the questions that contain at least one of the
                 searched keywords in either their title, body, or tag fields
        """
        query = {'$text': {
            '$search': keywords
        }}
        return list(self.posts.find(query))

    def increment_view_count(self, question_data):
        """
        Increments the view count of a specified question by 1.
        :param question_data: dict corresponding to document of question post increment the view count of
        :return: dict corresponding to the updated document of the question post (ViewCount value has been incremented)
        """
        query = {'_id': question_data['_id']}
        update = {'$inc': {'ViewCount': 1}}
        self.posts.update_one(query, update)
        return self.posts.find_one(query)

    def add_answer(self, question_id, body, user_id, content_license='CC BY-SA 2.5'):
        """
        Adds an answer post to the Posts collection.
        :param question_id: value of the Id field of the question that this answer is answering
        :param body: answer text
        :param user_id: id of user who is posting the answer (if None the answer post that is added to the Posts
                        collection will not have a OwnerUserId field)
        :param content_license: 'CC BY-SA 2.5' by default
        """
        if user_id is not None:
            insertion = {
                'Id': self._get_new_id('post'),
                'PostTypeId': ANSWER_TYPE_ID,
                'ParentId': question_id,
                'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3],
                'Score': 0,
                'Body': body,
                'OwnerUserId': str(user_id),
                'CommentCount': 0,
                'ContentLicense': content_license
            }
        else:
            insertion = {
                'Id': self._get_new_id('post'),
                'PostTypeId': ANSWER_TYPE_ID,
                'ParentId': question_id,
                'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3],
                'Score': 0,
                'Body': body,
                'CommentCount': 0,
                'ContentLicense': content_license
            }
        write_res = self.posts.insert_one(insertion)

    def get_answers(self, question_data):
        """
        Gets the answers to the specified question. If the question has an accepted answer the accepted answer will
        be put as the first element in the list.
        :param question_data: dict corresponding to document of question post to get the answers of
        :return: tuple of bool, list of dicts where the bool corresponds to whether the first element of the list is the
                 accepted answer (True if so) and the list corresponds to all the answers to the specified question
        """
        if 'AcceptedAnswerId' in question_data:
            accepted_ans_query = {'Id': question_data['AcceptedAnswerId']}
            accepted_ans = self.posts.find_one(accepted_ans_query)
            query = {'$and': [
                {'Id': {'$ne': accepted_ans['Id']}},
                {'PostTypeId': ANSWER_TYPE_ID},
                {'ParentId': question_data['Id']}
            ]}
            return True, [accepted_ans] + list(self.posts.find(query))
        else:
            query = {'$and': [
                {'PostTypeId': ANSWER_TYPE_ID},
                {'ParentId': question_data['Id']}
            ]}
            return False, list(self.posts.find(query))

    def check_vote_eligibility(self, post_data, user_id):
        """
        Checks to see whether a user id is eligible to vote on a post (i.e. they have not yet voted on the post).
        :param post_data: dict corresponding to document of post to add a vote to
        :param user_id: user id to add a vote from
        :return: True if the user id has not yet voted on the specified post (i.e. they are eligible), False otherwise
        """
        query = {'$and': [
            {'PostId': post_data['Id']},
            {'UserId': str(user_id)}
        ]}
        return True if self.votes.find_one(query) is None else False

    def add_vote(self, post_data, user_id):
        """
        Adds a vote from the specified user on the specified post to the Votes collection and increments the score of
        the post by one.
        :param post_data: dict corresponding to document of post to add a vote to
        :param user_id: user id to add a vote from (if a value of None is passed, there will be no UserId field in the
                        document inserted into the Votes collection)
        """
        if user_id is not None:
            insertion = {
                'Id': self._get_new_id('vote'),
                'PostId': post_data['Id'],
                'VoteTypeId': '2',
                'UserId': str(user_id),
                'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3]
            }
        else:
            insertion = {
                'Id': self._get_new_id('vote'),
                'PostId': post_data['Id'],
                'VoteTypeId': '2',
                'CreationDate': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.') + datetime.now().strftime('%f')[:3]
            }
        write_res = self.votes.insert_one(insertion)

        query = {'_id': post_data['_id']}
        update = {'$inc': {'Score': 1}}
        self.posts.update_one(query, update)

    def close(self):
        self.client.close()
