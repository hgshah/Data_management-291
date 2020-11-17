import sys
from screens import *
from db_manager import DBManager

DB_NAME = '291db'


class Operator:
    """
    TODO
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def run(self):
        start = StartScreen(self.db_manager)
        user_id, report_info = start.run()
        main_menu = MainMenu(self.db_manager, user_id, report_info)
        main_menu.run()
        self.db_manager.close()


if __name__ == '__main__':
    assert (len(sys.argv) == 2), 'please enter the correct number of arguments - this program should be run using ' \
                                 '"python3 phase2.py PORT_NUMBER"'
    try:
        port = int(sys.argv[1])
        dbm = DBManager(port)
        Operator(dbm).run()
    except ValueError:
        assert False, 'ValueError - please ensure that the port number specified is an integer'
