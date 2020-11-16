import os


def clear_screen():
    """
    Clears the current shell screen.
    """
    os.system('clear')


def select_from_menu(valid_inputs):
    """
    This allows a user to enter an input from a selection of values denoted by valid_inputs. It is assumed that the
    "menu" is already printed as this function just grabs the users input and checks if it is in the passed list
    valid_inputs (therefore being valid). If the input is invalid the user is prompted to make another selection
    until a valid input is entered.
    :param valid_inputs: list including all the inputs that should be considered valid
    :return: a string corresponding to the users valid selection
    """
    selection = input('> ')
    while selection not in valid_inputs:
        print('"{}" is an invalid selection, please enter a valid selection from the menu above.'
              .format(selection))
        selection = input('> ')
    return selection


class BaseScreen:
    """
    Base class representing a screen. Child classes must implement the _setup and run methods described below.
    """

    def __init__(self, db_manager=None):
        """
        Clears the screen upon initialization and runs the child class' _setup method.
        :param db_manager: sqlite database manager (optional parameter)
        """
        self.db_manager = None if db_manager is None else db_manager
        clear_screen()
        self._setup()

    def _setup(self):
        """
        This should print out the screen title and options that the screen supports. Called in the constructor. Must be
        implemented by subclass.
        """
        return NotImplementedError

    def run(self):
        """
        This should run the functionality supported by the screen. Must be implemented by subclass.
        """
        return NotImplementedError


class StartScreen(BaseScreen):

    def __init__(self, db_manager):
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        print('Would you like to provide a user id?\n'
              '\t[1] Yes\n'
              '\t[2] No')

    def run(self):
        user_id = None
        valid_inputs = ['1', '2']
        selection = select_from_menu(valid_inputs)
        if selection == '1':
            try:
                user_id = int(input('Please enter the user id that you would like to use:\n> '))
                invalid = False
            except ValueError:
                invalid = True
            while invalid:
                try:
                    user_id = int(input('Invalid input - user id must be numeric. Please try again:\n> '))
                    invalid = False
                except ValueError:
                    invalid = True
            num_owned_qs, avg_q_score = self.db_manager.get_num_owned_questions_and_avg_score(user_id)
            num_owned_as, avg_a_score = self.db_manager.get_num_owned_answers_and_avg_score(user_id)
            num_votes = self.db_manager.get_num_votes(user_id)
            return user_id, [num_owned_qs, avg_q_score, num_owned_as, avg_a_score, num_votes]
        else:
            return user_id, {}


class MainMenu(BaseScreen):
    def __init__(self, db_manager, user_id, report_info):
        self.user_id = user_id
        self.report_info = report_info
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        print('MAIN MENU\n\nWelcome {}!'.format('anonymous' if self.user_id is None else self.user_id))
        if len(self.report_info) == 5:
            print(
                '\tNumber of owned questions: {}\n'
                '\tAverage score of owned questions: {}\n'
                '\tNumber of owned answers: {}\n'
                '\tAverage score of owned answers: {}\n'
                '\tNumber of votes registered for you: {}'.format(
                    self.report_info[0],
                    self.report_info[1],
                    self.report_info[2],
                    self.report_info[3],
                    self.report_info[4]
                )
            )
        # TODO print options

    def run(self):
        # TODO run options
        pass
