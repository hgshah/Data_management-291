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
        self.db = self.client['DB_NAME']
        self.posts, self.tags, self.votes = self.db['Posts'], self.db['Tags'], self.db['Votes']

    def get_num_owned_posts_and_avg_score(self, user_id, post_type):
        """
        TODO
        :param user_id:
        :param post_type: int corresponding to the post type (1 if post type is question and 2 if post type is answer)
        :return:
        """
        owned_questions_pipeline = [
            {'$match': {'$and': [{'PostTypeId': str(post_type)}, {'OwnerUserId': str(user_id)}]}},
            {'$count': 'owned_questions'}
        ]
        res1 = self.posts.aggregate(owned_questions_pipeline)
        print(res1.next())
        avg_score_pipeline = [
            {'$match': {'$and': [{'PostTypeId': str(post_type)}, {'OwnerUserId': str(user_id)}]}},
            {'$group': {'_id': {'user_id': '$OwnerUserId'}, 'avg_score': {'$avg': '$Score'}}}
        ]
        res2 = self.posts.aggregate(avg_score_pipeline)
        print(res2.next())
        return None, None

    def get_num_votes(self, user_id):
        """
        TODO
        :param user_id:
        :return:
        """
        num_votes_pipeline = [
            {'$match': {'OwnerUserId': str(user_id)}},
            {'$group': {'_id': {'user_id': '$OwnerUserId'}, 'num_votes': {'$sum': '$Score'}}}
        ]
        res = self.posts.aggregate(num_votes_pipeline)
        for i in res:
            print(i)
        exit(0)

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
