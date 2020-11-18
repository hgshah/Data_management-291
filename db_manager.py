from pymongo import MongoClient

DB_NAME = '291db'


class DBManager:
    """
    TODO
    """

    def __init__(self, port):
        """
        Gets a pymongo database with name DB_NAME.
        :param port:
        """
        self.client = MongoClient(port=port)
        self.db = self.client[DB_NAME]
        self.posts, self.tags, self.votes = self.db['Posts'], self.db['Tags'], self.db['Votes']

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
        query = {'OwnerUserId': str(user_id)}
        proj = {'Id': True, '_id': False}
        res1 = list(self.posts.find(query, projection=proj))
        if len(res1) == 0:
            return 0
        post_ids = [post_id['Id'] for post_id in res1]
        print(res1, post_ids)
        num_votes_pipeline = [
            {'$match': {'PostId': {'$in', res1}}},
            {'$count': 'num_votes'}
        ]
        res2 = list(self.votes.aggregate(num_votes_pipeline))
        print(res2)
        return 0 if len(res2) != 1 else res2[0]['num_votes']

    def add_post(self, title, body, tags, post_type, user_id, content_license='CC BY-SA 2.5'):
        # TODO create unique id
        # TODO set creation date to current date
        # post_type should be 1 for a question and 2 for an answer
        score, view_count, answer_count, cmt_count, fav_count = 0, 0, 0, 0, 0
        pass

    def get_search_results(self, keywords):
        pass

    def increment_view_count(self, question_id):
        pass

    def add_answer(self, question_id, body, user_id):
        pass

    def get_answers(self, question_id):
        pass

    def check_vote_eligibility(self, post_id, user_id):
        pass

    def add_vote(self, post_id, user_id):
        # TODO create unique vote id
        # TODO set creation date to current date
        # vote type id should be 2
        # TODO update score field in Posts
        pass

    def close(self):
        self.client.close()
