from pymongo import MongoClient
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
        self.posts, self.tags, self.votes = self.db['Posts'], self.db['Tags'], self.db['Votes']

    # def _create_search_index(self):
    #     """
    #     Creates a search index with the Title, Body, and Tags fields in the Posts collection.
    #     """
    #     if SEARCH_INDEX not in list(self.posts.list_indexes()):
    #         print('Creating search index...')
    #         keys = [('Title', TEXT), ('Body', TEXT), ('Tags', TEXT)]
    #         self.posts.create_index(keys, name=SEARCH_INDEX)

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

    def add_post(self, title, body, tags, post_type, user_id, content_license='CC BY-SA 2.5'):
        # TODO create unique id
        # TODO set creation date to current date
        # post_type should be 1 for a question and 2 for an answer
        score, view_count, answer_count, cmt_count, fav_count = 0, 0, 0, 0, 0
        pass

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
        update = {'$inc': {'ViewCount': 1}} if 'ViewCount' in question_data else {'$set': {'ViewCount': 1}}
        self.posts.update_one(query, update)
        return self.posts.find_one(query)

    def add_answer(self, question_id, body, user_id):
        pass

    def get_answers(self, question_data):
        if 'AcceptedAnswerId' in question_data:
            accepted_ans_query = {'Id': question_data['AcceptedAnswerId']}
            accepted_ans = self.posts.find_one(accepted_ans_query)
            query = {'$and': [
                {'Id': {'$ne': accepted_ans['Id']}},
                {'PostTypeId': ANSWER_TYPE_ID},
                {'ParentId': question_data['Id']}
            ]}
            return True, [accepted_ans] + list(self.posts.find(query)) #TODO try with q that has no a
        else:
            query = {'$and': [
                {'PostTypeId': ANSWER_TYPE_ID},
                {'ParentId': question_data['Id']}
            ]}
            return False, list(self.posts.find(query))

    def check_vote_eligibility(self, post_id, user_id):
        query = {'$and': [
            {'PostId': post_id},
            {'UserId': str(user_id)}
        ]}
        res = self.votes.find_one(query)
        print(res)


    def add_vote(self, post_id, user_id):
        # TODO create unique vote id
        # TODO set creation date to current date
        # vote type id should be 2
        # TODO update score field in Posts
        pass

    def close(self):
        self.client.close()
