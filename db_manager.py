from pymongo import MongoClient, ASCENDING, collation
from datetime import datetime
import re

DB_NAME = '291db'
SEARCH_INDEX = 'search_index'
QUESTION_TYPE_ID = '1'
ANSWER_TYPE_ID = '2'


class DBManager:
    """
    TODO
    """

    def __init__(self, port):
        """
        Gets a pymongo database with name DB_NAME. Also creates an index on the posts collection to be used for
        searches.
        :param port:
        """
        self.client = MongoClient(port=port)
        self.db = self.client[DB_NAME]
        self.postId_index, self.tagId_index, self.voteId_index = 'post_Id_index', 'tag_Id_index', 'vote_Id_index'
        self.post_owner_index = 'post_owner_index'
        self.posts, self.tags, self.votes = self.db['Posts'], self.db['Tags'], self.db['Votes']
        self._try_creating_indexes()

    def _try_creating_indexes(self):
        post_indexes = self.posts.list_indexes()
        tag_indexes = self.tags.list_indexes()
        vote_indexes = self.votes.list_indexes()
        print('Creating indexes...')
        if self.postId_index not in post_indexes:
            self.posts.create_index(
                [('Id', ASCENDING)],
                collation=collation.Collation('en_US', numericOrdering=True),
                name=self.postId_index
            )
        if self.post_owner_index not in post_indexes:
            self.posts.create_index([('PostTypeId', ASCENDING), ('OwnerUserId', ASCENDING)], name=self.post_owner_index)
        if self.tagId_index not in tag_indexes:
            self.tags.create_index(
                [('Id', ASCENDING)],
                collation=collation.Collation('en_US', numericOrdering=True),
                name=self.tagId_index
            )
        if self.voteId_index not in vote_indexes:
            self.votes.create_index(
                [('Id', ASCENDING)],
                collation=collation.Collation('en_US', numericOrdering=True),
                name=self.voteId_index
            )

    def _get_new_id(self, id_type):
        # res = []
        # max_id_pipeline = [{'$group': {'_id': None, 'max_id': {'$max': {'$toInt': '$Id'}}}}]
        max_id_query = {'Id': -1}
        if id_type == 'post':
            res = self.posts.find_one(
                sort=max_id_query,
                limit=1,
                collation=collation.Collation('en_US', numericOrdering=True)
            )
            # res = list(self.posts.aggregate(max_id_pipeline))
        elif id_type == 'vote':
            res = self.votes.find_one(
                sort=max_id_query,
                limit=1,
                collation=collation.Collation('en_US', numericOrdering=True)
            )
            # res = list(self.votes.aggregate(max_id_pipeline))
        elif id_type == 'tag':
            res = self.tags.find_one(
                sort=max_id_query,
                limit=1,
                ollation=collation.Collation('en_US', numericOrdering=True)
            )
            # res = list(self.tags.aggregate(max_id_pipeline))
        # max_id = 0 if len(res) != 1 else res[0]['max_id']
        # return str(max_id + 1)
        return res['Id']

    def _assemble_tag_string(self, tags):
        if len(tags) == 0:
            return None
        tag_string = ''
        for tag in tags:
            tag_string += '<' + tag + '>'
            res = self.tags.find_one({'TagName': tag})
            if res is None:
                write_res = self.tags.insert_one({'Id': self._get_new_id('tag'), 'TagName': tag, 'Count': 1})
            else:
                self.tags.update_one({'_id': res['_id']}, {'$inc': {'Count': 1}})
        return tag_string

    def get_num_owned_posts_and_avg_score(self, user_id, post_type):
        """
        TODO
        :param user_id:
        :param post_type: int corresponding to the post type (1 if post type is question and 2 if post type is answer)
        :return:
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
        TODO
        :param user_id:
        :return:
        """
        num_votes_pipeline = [
            {'$match': {'UserId': str(user_id)}},
            {'$count': 'num_votes'}
        ]
        res2 = list(self.votes.aggregate(num_votes_pipeline))
        return 0 if len(res2) != 1 else res2[0]['num_votes']

    def add_question(self, title, body, tags, user_id, content_license='CC BY-SA 2.5'):
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
        regx_keywords = []
        for keyword in keywords:
            regx_keywords.append(re.compile('.*' + keyword + '.*', flags=re.IGNORECASE | re.DOTALL))
        query = {'$and': [
            {'PostTypeId': QUESTION_TYPE_ID},
            {'$or': [
                {'Title': {'$in': regx_keywords}},
                {'Tags': {'$in': regx_keywords}},
                {'Body': {'$in': regx_keywords}}
            ]}
        ]}
        return list(self.posts.find(query))

    def increment_view_count(self, question_data):
        query = {'_id': question_data['_id']}
        update = {'$inc': {'ViewCount': 1}}
        self.posts.update_one(query, update)
        return self.posts.find_one(query)

    def add_answer(self, question_id, body, user_id, content_license='CC BY-SA 2.5'):
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
        query = {'$and': [
            {'PostId': post_data['Id']},
            {'UserId': str(user_id)}
        ]}
        return True if self.votes.find_one(query) is None else False

    def add_vote(self, post_data, user_id):
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
