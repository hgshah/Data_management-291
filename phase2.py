import sys
from screens import *
from db_manager import DBManager

DB_NAME = '291db'


class Driver:
    """
    TODO
    """

    def __init__(self, port):
        self.db_manager = DBManager(port)

    def run(self):
        user_id, report_info = StartScreen(self.db_manager).run()
        MainMenu(self.db_manager, user_id, report_info).run()
        self.db_manager.close()
        clear_screen()


if __name__ == '__main__':
    assert (len(sys.argv) == 2), 'please enter the correct number of arguments - this program should be run using ' \
                                 '"python3 phase2.py PORT_NUMBER"'
    try:
        port_no = int(sys.argv[1])
        Driver(port_no).run()
    except ValueError:
        assert False, 'ValueError - please ensure that the port number specified is an integer'
