import sys
from db_manager import DBManager


class PostStore:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def run(self):
        pass


if __name__ == '__main__':
    assert (len(sys.argv) == 2), 'please enter the correct number of arguments - this program should be run using ' \
                                 '"python3 prj.py PORT_NUMBER"'
    try:
        port = int(sys.argv[1])
        p = PostStore(DBManager(port))
        p.run()
    except ValueError:
        assert False, 'ValueError - please ensure that the port number specified is an integer'
