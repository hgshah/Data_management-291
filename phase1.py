import json
import sys
from os import path
from pymongo import MongoClient

DB_NAME = '291db'
POSTS_FILE = 'Posts.json'
TAGS_FILE = 'Tags.json'
VOTES_FILE = 'Votes.json'


class BuildDocStore:
    """
    Class that connects to the specified MongoDB server, creates a database named "291db" (if it does not exist), and 
    then creates three collections named Posts, Tags, and Votes.
    """

    def __init__(self, port):
        self.client = MongoClient(port=port)
        self.db = self.client[DB_NAME]
        self._drop_collections()
        self.posts, self.tags, self.votes = self.db['Posts'], self.db['Tags'], self.db['Votes']
        self._populate_collections()
        self._close()

    def _drop_collections(self):
        """
        Drops the three collections named Posts, Tags, and Votes if they already exist.
        """
        assert path.exists(POSTS_FILE), 'no "Posts.json" file exists in the current directory'
        assert path.exists(TAGS_FILE), 'no "Tags.json" file exists in the current directory'
        assert path.exists(VOTES_FILE), 'no "Votes.json" file exists in the current directory'
        coll_names = ['Posts', 'Tags', 'Votes']
        coll_list = self.db.list_collection_names()
        for name in coll_names:
            if name in coll_list:
                self.db.drop_collection(name)

    def _populate_collections(self):
        """
        Populates the Posts, Tags, and Votes collections with the data in Posts.json, Tags.json, and Votes.json
        respectively.
        """
        with open(POSTS_FILE) as p:
            p_data = json.load(p)
        with open(TAGS_FILE) as t:
            t_data = json.load(t)
        with open(VOTES_FILE) as v:
            v_data = json.load(v)
        p_res = self.posts.insert_many(p_data['posts']['row'])
        t_res = self.tags.insert_many(t_data['tags']['row'])
        v_res = self.votes.insert_many(v_data['votes']['row'])

    def _close(self):
        self.client.close()


if __name__ == '__main__':
    assert (len(sys.argv) == 2), 'please enter the correct number of arguments - this program should be run using ' \
                                 '"python3 phase1.py PORT_NUMBER"'
    try:
        p = int(sys.argv[1])
        BuildDocStore(p)
    except ValueError:
        assert False, 'ValueError - please ensure that the port number specified is an integer'
