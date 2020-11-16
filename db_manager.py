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

    def close(self):
        self.client.close()
