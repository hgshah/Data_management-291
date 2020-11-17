from pymongo import MongoClient

DB_NAME = '291db'


class DBManager:
    """
    TODO
    """

    def __init__(self, port):
        self.client = MongoClient(port=port)
        self.db = self._get_db()

    def _get_db(self):
        """
        Gets a pymongo database with name DB_NAME.
        :return: a pymongo.database.Database object with the name DB_NAME
        """
        if DB_NAME not in self.client.list_database_names():
            return self.client.get_database(name=DB_NAME)
        else:
            return self.client[DB_NAME]

    def get_num_owned_questions_and_avg_score(self, user_id):
        """
        TODO
        :param user_id:
        :return:
        """
        pass

    def get_num_owned_answers_and_avg_score(self, user_id):
        """
        TODO
        :param user_id:
        :return:
        """
        pass

    def get_num_votes(self, user_id):
        """
        TODO
        :param user_id:
        :return:
        """
        pass

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
