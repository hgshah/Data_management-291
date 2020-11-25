import os

MAX_PER_PAGE = 10


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
    while selection.lower() not in valid_inputs:
        print('"{}" is an invalid selection, please enter a valid selection from the menu above.'
              .format(selection))
        selection = input('> ')
    return selection.lower()


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

    def _try_adding_vote(self, post_data, user_id):
        """
        Tries to add a vote of type 2 on the specified post from the the specified user. Ensures that the user is
        eligible before adding the vote - if the user is not eligible the vote is not added and the user is notified
        why they were ineligible (a user who has specified a user id can only vote once per post whereas a user who
        has not specified a user id can vote as many times as they would like).
        :param post_data: dict corresponding to the Post document to add a vote to
        :param user_id: int representing user id of user or None if they did not specify one
        """
        clear_screen()
        print('ADD VOTE')
        if user_id is not None:
            eligible = self.db_manager.check_vote_eligibility(post_data, user_id)
            if not eligible:
                input('\nInvalid action requested...\n'
                      'You have already voted on this post so you are not eligible to vote again - please enter any key'
                      ' to return to the main menu:\n> ')
                return
        self.db_manager.add_vote(post_data, user_id)
        input('\nSuccessfully added your vote to the post - please enter any key to return to the main menu:\n> ')

    def run(self):
        """
        This should run the functionality supported by the screen. Must be implemented by subclass.
        """
        return NotImplementedError


class StartScreen(BaseScreen):
    """
    Class representing the start screen. Allows the user to provide a user id if they wish.
    """

    def __init__(self, db_manager):
        """
        Initializes a Main Menu object.
        :param db_manager: an instance of the db_manager.DBManager class
        """
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        print('START SCREEN')
        print('\nWould you like to provide a user id?\n'
              '\t[1] Yes\n'
              '\t[2] No')

    def run(self):
        """
        Gives the user the option to specify a user id and if they decide to ensures that the specified user id is
        numeric and gets the required data for the user report (num owned questions, avg score of owned questions, num
        owned answers, avg score of owned answers, num votes registered by user).
        :return: tuple consisting of (int, list) where the int corresponds to the specified user id (or a None value if
                 they did not want to provide one) and the list corresponds to [number of owned questions, avg score of
                 owned questions, number of owned answers, avg score of owned answers, number of votes registered] for
                 the user id (or an empty list if they did not provide one)
        """
        user_id = None
        valid_inputs = ['1', '2']
        selection = select_from_menu(valid_inputs)
        if selection == '1':
            try:
                user_id = int(input('\nPlease enter the user id that you would like to use:\n> '))
                invalid = False
            except ValueError:
                invalid = True
            while invalid:
                try:
                    user_id = int(input('Invalid input - user id must be numeric. Please try again:\n> '))
                    invalid = False
                except ValueError:
                    invalid = True
            num_owned_qs, avg_q_score = self.db_manager.get_num_owned_posts_and_avg_score(user_id, 1)
            num_owned_as, avg_a_score = self.db_manager.get_num_owned_posts_and_avg_score(user_id, 2)
            num_votes = self.db_manager.get_num_votes(user_id)
            return user_id, [num_owned_qs, avg_q_score, num_owned_as, avg_a_score, num_votes]
        elif selection == '2':
            return user_id, []


class MainMenu(BaseScreen):
    """
    Class representing the main menu screen. If the user has specified a user id they are shown a report that includes
    the number of questions owned and the average score for those questions, the number of answers owned and the average
    score for those answers, and the number of votes registered for the user.
    """

    def __init__(self, db_manager, user_id, report_info):
        """
        Initializes a Main Menu object.
        :param db_manager: an instance of the db_manager.DBManager class
        :param user_id: user id specified by the user (if they did not specify one pass a None value)
        :param report_info: list corresponding to [number of owned questions, avg score of owned questions, number of
                            owned answers, avg score of owned answers, number of votes registered] for the user id
                            specified (if they did not specify one pass an empty list)
        """
        self.user_id = user_id
        self.report_info = report_info
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        """
        Displays a report if a user id was specified and displays the main menu options (post a question, search for
        questions, end program).
        """
        print('MAIN MENU\n\nWelcome {}!'.format('anonymous' if self.user_id is None else self.user_id))
        if len(self.report_info) == 5:
            print(
                '\nNumber of owned questions: {}\n'
                'Average score for owned questions: {}\n'
                'Number of owned answers: {}\n'
                'Average score for owned answers: {}\n'
                'Number of votes registered for you: {}'.format(
                    self.report_info[0],
                    self.report_info[1],
                    self.report_info[2],
                    self.report_info[3],
                    self.report_info[4]
                )
            )
        print('\nPlease select the task you would like to perform:\n'
              '\t[1] Post a question\n'
              '\t[2] Search for questions\n'
              '\t[e] End program')

    def _refresh(self):
        """
        Clears the shell screen and gets the an updated version of the required data for the user report (num owned
        questions, avg score of owned questions, num owned answers, avg score of owned answers, num votes registered by
        user) if a user id was specified.
        """
        clear_screen()
        if self.user_id is not None:
            num_owned_qs, avg_q_score = self.db_manager.get_num_owned_posts_and_avg_score(self.user_id, 1)
            num_owned_as, avg_a_score = self.db_manager.get_num_owned_posts_and_avg_score(self.user_id, 2)
            num_votes = self.db_manager.get_num_votes(self.user_id)
            self.report_info = [num_owned_qs, avg_q_score, num_owned_as, avg_a_score, num_votes]
        self._setup()

    def run(self):
        """
        Gives the user the option to either post a question or search for questions and carries out the corresponding
        action. Repeats until the user decides to end the program.
        """
        valid_inputs = ['1', '2', 'e']
        while True:
            selection = select_from_menu(valid_inputs)
            if selection == '1':
                PostQuestion(self.db_manager, self.user_id).run()
            elif selection == '2':
                SearchForQuestions(self.db_manager, self.user_id).run()
            elif selection == 'e':
                break
            self._refresh()


class PostQuestion(BaseScreen):
    """
    Class representing the post question screen. Allows the user to post a question which will be added to the database.
    """

    def __init__(self, db_manager, user_id):
        """
        Initializes an instance of this class.
        :param db_manager: an instance of the db_manager.DBManager class
        :param user_id: user id specified by the user (if they did not specify one pass a None value)
        """
        self.user_id = user_id
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        print('POST QUESTION')

    def run(self):
        """
        Allows the user to post a question by providing a title, body, and zero or more tags. Prints a confirmation
        once completed.
        """
        valid_inputs = ['1', '2']
        tags = []
        title = input('\nPlease enter the title of the question you would like to post:\n> ')
        body = input('\nPlease enter the body of the question you would like to post:\n> ')
        print('\nWould you like to add tag(s)?\n'
              '\t[1] Yes\n'
              '\t[2] No')
        selection = select_from_menu(valid_inputs)
        while selection == '1':
            tag = input('Enter the tag you would like to add:\n> ')
            tags.append(tag)
            print('\nWould you like to add another tag?\n'
                  '\t[1] Yes\n'
                  '\t[2] No')
            selection = select_from_menu(valid_inputs)
        self.db_manager.add_question(title, body, tags, self.user_id)
        clear_screen()
        print('POST QUESTION')
        input('\nQuestion successfully posted - please enter any key to return to the main menu:\n> ')


class SearchForQuestions(BaseScreen):
    """
    Class representing the search for questions screen. Allows the user to provide one or more space separated keywords
    that they would like to search.
    """

    def __init__(self, db_manager, user_id):
        """
        Initializes an instance of this class.
        :param db_manager: an instance of the db_manager.DBManager class
        :param user_id: user id specified by the user (if they did not specify one pass a None value)
        """
        self.user_id = user_id
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        print('SEARCH FOR QUESTIONS')

    def run(self):
        """
        Allows the user to provide one or more space separated keywords which are passed to the SearchResults screen
        which retrieves the results.
        """
        keywords = input('\nPlease enter a space separated list of one or more keywords:\n> ')
        while len(keywords) == 0:
            keywords = input('Invalid input - you must enter at least one keyword:\n> ')
        SearchResults(self.db_manager, self.user_id, keywords).run()


class SearchResults(BaseScreen):
    """
    Class representing the search results screen. Retrieves and displays (up to 10 at a time) all questions that contain
    at least one of the searched keywords in either title, body, or tag fields (case-insensitive).
    """

    def __init__(self, db_manager, user_id, keywords):
        """
        Initializes an instance of this class.
        :param db_manager: an instance of the db_manager.DBManager class
        :param user_id: user id specified by the user (if they did not specify one pass a None value)
        :param keywords: a string containing the space-separated keywords to search as elements
        """
        self.valid_inputs = []
        self.user_id = user_id
        BaseScreen.__init__(self, db_manager=db_manager)
        self.search_res = self.db_manager.get_search_results(keywords)

    def _setup(self):
        print('SEARCH RESULTS')

    def _display_search_results(self, current_ind):
        """
        Displays up to 10 search results at a time. Displays the title, creation date, score, and answer count of each
        retrieved question.
        :param current_ind: integer representing the number of search results that have already been displayed
        :return: None if all search results have been printed or the number of search results that have been printed
        """
        self.valid_inputs = []
        clear_screen()
        self._setup()
        for i in range(MAX_PER_PAGE):
            ind = i + current_ind
            if ind + 1 > len(self.search_res):
                return None
            self.valid_inputs.append(str(ind + 1))
            q = self.search_res[ind]
            print(
                '\n[{}] {}\n'
                '\tCreationDate: {}\tScore: {}\tAnswerCount: {}'.format(
                    ind + 1, q['Title'], q['CreationDate'], q['Score'], q['AnswerCount']
                )
            )
        return MAX_PER_PAGE

    def run(self):
        """
        Displays the search results (up to 10 at a time) and gives the user the option to select a question to perform
        an action on, see more search results (if possible), or return to the main menu.
        """
        current_ind = 0
        while True:
            num_printed = self._display_search_results(current_ind)
            if (num_printed is None) or (current_ind + num_printed == len(self.search_res)):
                print(
                    '\nPlease select the action that you would like to take:\n'
                    '\t[#] Enter the number corresponding to the question that you would like to perform an action on\n'
                    '\t[r] Return to the main menu'
                )
                selection = select_from_menu(self.valid_inputs + ['r'])
            else:
                current_ind += num_printed
                print(
                    '\nPlease select the action that you would like to take:\n'
                    '\t[#] Enter the number corresponding to the question that you would like to perform an action on\n'
                    '\t[m] See more search results\n'
                    '\t[r] Return to the main menu'
                )
                selection = select_from_menu(self.valid_inputs + ['m', 'r'])
            if selection != 'm':
                break
        if selection != 'r':
            QuestionAction(self.db_manager, self.user_id, self.search_res[int(selection) - 1]).run()


class QuestionAction(BaseScreen):
    """
    Class representing the question action screen. Displays all the fields of the selected question an allows the user
    to either answer the selected question, list existing answers to the selected question, add a vote to the selected
    question, or return to the main menu.
    """

    def __init__(self, db_manager, user_id, selected_question_data):
        """
        Initializes an instance of this class.
        :param db_manager: an instance of the db_manager.DBManager class
        :param user_id: user id specified by the user (if they did not specify one pass a None value)
        :param selected_question_data: a dict containing the data of the selected question post
        """
        self.user_id = user_id
        self.question_data = selected_question_data
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        """
        Increments the view count of the selected question by one and then displays the possible question actions that
        the user can take.
        """
        self.question_data = self.db_manager.increment_view_count(self.question_data)
        print('QUESTION ACTION\n')
        for key, value in self.question_data.items():
            print('{} : {}'.format(key, value))
        print(
            '\nPlease select the action that you would like to take:\n'
            '\t[1] Answer the question\n'
            '\t[2] List existing answers\n'
            '\t[3] Add a vote\n'
            '\t[r] Return to the main menu'.format(
                self.question_data['Title'],
                self.question_data['CreationDate'],
                self.question_data['Score'],
                self.question_data['AnswerCount']
            )
        )

    def _answer_question(self):
        """
        Allows the user to provide an answer text and then adds a new answer post to the database accordingly. Prints
        a confirmation upon completion allowing the user to return to the main menu.
        """
        clear_screen()
        print('ANSWER QUESTION')
        body = input('\nPlease enter the text corresponding to your answer:\n> ')
        self.db_manager.add_answer(self.question_data['Id'], body, self.user_id)
        clear_screen()
        print('ANSWER QUESTION')
        input('\nAnswer successfully posted - please enter any key to return to the main menu:\n> ')

    def _display_answers(self, current_ind, answers, has_accepted):
        """
        Displays the up to 10 answers (at a time) to the selected question. If the question has an accepted answer it
        is displayed first and is marked with a star. Shows up to the first 80 characters of the body text, the creation
        date, and the score of each answer.
        :param current_ind: integer representing the number of search results that have already been displayed
        :param answers: a list containing the data of each answer to the selected question
        :param has_accepted: whether the first index (current_ind + i) is an accepted answer
        :return: tuple consisting of int, list where the int is either None if all search results have been printed or
                 the number of search results that have been printed and the list is the valid inputs for the answers
                 that have just been printed (i.e. if answers 11-20 have just been printed the list would be ['11',
                 '12', '13', '14', '15', '16', '17', '18', '19', '20']
        """
        valid_inputs = []
        clear_screen()
        print('EXISTING ANSWERS')
        for i in range(MAX_PER_PAGE):
            ind = i + current_ind
            if ind + 1 > len(answers):
                return None, valid_inputs
            valid_inputs.append(str(ind + 1))
            a = answers[ind]
            if has_accepted and (i == 0):
                print('\n[{}]******************************\n'
                      '{}\n'
                      'CreationDate: {}\n'
                      'Score: {}'.format(ind + 1, a['Body'][:80], a['CreationDate'], a['Score']))
            else:
                print('\n[{}]------------------------------\n'
                      '{}\n'
                      'CreationDate: {}\n'
                      'Score: {}'.format(ind + 1, a['Body'][:80], a['CreationDate'], a['Score']))
        return MAX_PER_PAGE, valid_inputs

    def _list_answers(self):
        """
        Displays the answers to the selected question (up to 10 at a time) and gives the user the option to select an
        answer to perform an action on, see more answers (if possible), or return to the main menu. If the selected
        question has an accepted answer it will be displayed first and will be marked with a star.
        """
        has_accepted, answers = self.db_manager.get_answers(self.question_data)
        current_ind = 0
        while True:
            num_printed, valid_inputs = self._display_answers(current_ind, answers, has_accepted)
            has_accepted = False
            if (num_printed is None) or (current_ind + num_printed == len(answers)):
                print(
                    '\nPlease select the action that you would like to take:\n'
                    '\t[#] Enter the number corresponding to the answer that you would like to perform an action on\n'
                    '\t[r] Return to the main menu'
                )
                selection = select_from_menu(valid_inputs + ['r'])
            else:
                current_ind += num_printed
                print(
                    '\nPlease select the action that you would like to take:\n'
                    '\t[#] Enter the number corresponding to the answer that you would like to perform an action on\n'
                    '\t[m] See more answers\n'
                    '\t[r] Return to the main menu'
                )
                selection = select_from_menu(valid_inputs + ['m', 'r'])
            if selection != 'm':
                break
        if selection != 'r':
            AnswerAction(self.db_manager, self.user_id, answers[int(selection) - 1]).run()

    def run(self):
        """
        Allows the user to either answer the selected question, list existing answers to the selected question, add a
        vote to the selected question, or return to the main menu.
        """
        valid_inputs = ['1', '2', '3', 'r']
        selection = select_from_menu(valid_inputs)
        if selection == '1':
            self._answer_question()
        elif selection == '2':
            self._list_answers()
        elif selection == '3':
            self._try_adding_vote(self.question_data, self.user_id)


class AnswerAction(BaseScreen):
    """
    Class representing the answer action screen. Displays all the fields of the selected answer and allows the user to
    either add a vote to the selected answer or return to the main menu.
    """

    def __init__(self, db_manager, user_id, selected_answer_data):
        """
        Initializes an instance of this class.
        :param db_manager: an instance of the db_manager.DBManager class
        :param user_id: user id specified by the user (if they did not specify one pass a None value)
        :param selected_answer_data: a dict containing the data of the selected answer post
        """
        self.user_id = user_id
        self.answer_data = selected_answer_data
        BaseScreen.__init__(self, db_manager=db_manager)

    def _setup(self):
        """
        Displays all the fields of the selected answer and the answer actions that the user is able to take.
        """
        print('ANSWER ACTION\n')
        for key, value in self.answer_data.items():
            print('{} : {}'.format(key, value))
        print('\nPlease select the action that you would like to take:\n'
              '\t[1] Add a vote\n'
              '\t[r] Return to the main menu')

    def run(self):
        """
        Allows the user to either add a vote to the selected answer or return to the main menu.
        """
        valid_inputs = ['1', 'r']
        selection = select_from_menu(valid_inputs)
        if selection != 'r':
            self._try_adding_vote(self.answer_data, self.user_id)
