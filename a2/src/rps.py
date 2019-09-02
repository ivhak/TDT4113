'''
Simulate rounds of Rock, Paper, Scissors
'''

from abc import ABC, abstractmethod
import getopt
import random
import sys
import os
import matplotlib.pyplot as plt
import argparser as ap

_ROCK = 0
_SCISSOR = 1
_PAPER = 2

_RAND = 0
_SEQ = 1
_HIST = 2
_FREQ = 3
_OTP = 4


class Player():
    '''
    Class representing a player with a given play style
    '''

    def __init__(self, play_style=_RAND, hist=0):

        # Choose a class to make action choices
        if play_style == _RAND:
            self.player_style = Rand()

        elif play_style == _SEQ:
            self.player_style = Seq()

        elif play_style == _HIST:
            self.player_style = History(hist_size=hist)

        elif play_style == _FREQ:
            self.player_style = Freq()

        elif play_style == _OTP:
            self.player_style = OneTrickPony()

        self.score = 0

    def get_result(self, opp_move=None, winner=None):
        ''' Get result of the last round played '''

        # If the player_style is history or freq, update the list of the
        # oppenents moves
        if isinstance(self.player_style, (Freq, History)):
            self.player_style.add_opp_move(int(opp_move))

        if winner is None:
            self.score += 0.5     # tie
        else:
            self.score += winner  # win = 1, lose = 0

    def get_name(self):
        ''' Name of player '''
        return self.player_style.get_name()

    def choose_action(self):
        ''' Get the next move from the player style object '''
        move = self.player_style.make_move()
        return Action(move)

    def get_score(self):
        ''' Return accumulated score'''
        return self.score

    def reset(self):
        ''' Reset modified values after a tournament '''
        self.score = 0
        self.player_style.reset()


class PlayerStyle(ABC):
    '''
    Abstract class  with methods that all the player style classes most
    implement
    '''
    @abstractmethod
    def make_move(self):
        ''' Get the move chosen by the given player style'''

    @abstractmethod
    def get_name(self):
        ''' Get the name/type of player type class'''

    @abstractmethod
    def reset(self):
        ''' Reset modified values after a tournament '''


class Rand(PlayerStyle):
    '''
    Select a move randomly each time
    '''

    def make_move(self):
        return random.randint(0, 2)

    def get_name(self):
        return 'Random'

    def reset(self):
        pass


class Seq(PlayerStyle):
    '''
    Play each move sequentially: rock, paper, scissors, rock, paper...
    '''

    def __init__(self):
        self.loop_count = 0

    def make_move(self):
        self.loop_count = (self.loop_count + 1) % 3
        return self.loop_count

    def get_name(self):
        return 'Sequential'

    def reset(self):
        self.loop_count = 0


class Freq(PlayerStyle):
    '''
    Choose the opposite move of the opponents most frequent move
    '''

    def __init__(self):
        self.move_count = [0, 0, 0]

    def make_move(self):
        if self.move_count == [0, 0, 0]:
            return random.randint(0, 2)

        # The index of the max value in move_count will be the move most often
        # done by the opponent -> return the move that beats this move:
        return (self.move_count.index(max(self.move_count)) - 1) % 3

    def add_opp_move(self, opp_move):
        ''' Update the list of the opponents moves '''
        self.move_count[int(opp_move)] += 1

    def get_name(self):
        return 'Frequency'

    def reset(self):
        self.move_count = [0, 0, 0]


class History(PlayerStyle):
    '''
    Keep a list of the opponents moves and check for the historically most
    likely move base on the hist_size last moves.
    '''

    def __init__(self, hist_size=0):
        self.opp_hist = []
        self.hist_size = hist_size

    def make_move(self):
        if len(self.opp_hist) < self.hist_size + 1:
            # History is not big enough yet, choose a random move
            return random.randint(0, 2)

        # Get the <hist_size> last moves done by the opponent
        last_moves = self.opp_hist[-self.hist_size:]

        # Count of how many times the moves came after these last moves
        # previously
        move_count = [0, 0, 0]

        # Loop through the history to find slices equal to <last_moves>, add
        # the move after a matching slice to move_count
        for i in range(len(self.opp_hist) - self.hist_size - 1):
            if self.opp_hist[i:i+self.hist_size] == last_moves:
                next_move = self.opp_hist[i+self.hist_size]
                move_count[next_move] += 1

        # The index of the max value in move_count will be the move most often
        # done after the last_moves -> return the move that beats this move:
        return (move_count.index(max(move_count)) - 1) % 3

    def add_opp_move(self, opp_move):
        ''' Update the list of the opponents moves '''
        self.opp_hist += [opp_move]

    def get_name(self):
        return 'Historical({})'.format(self.hist_size)

    def reset(self):
        self.opp_hist = []


class OneTrickPony(PlayerStyle):
    '''
    Dumbest strategy. Pick one move and stick to it
    '''

    def __init__(self):
        self.move = random.randint(0, 2)

    def make_move(self):
        return self.move

    def get_name(self):
        move_name = str(Action(self.move))
        return 'OneTrickPony({})'.format(move_name)

    def reset(self):
        pass


class Action():
    '''
    Class for representation of the moves in RPS
    '''

    def __init__(self, move=None):
        self.move = move

    def __eq__(self, ac2):
        return self.move == ac2.move

    def __gt__(self, ac2):
        # Rock beats scissors
        if (self.move == _ROCK and ac2.move == _SCISSOR):
            return True
        # Scissors beats paper
        if (self.move == _SCISSOR and ac2.move == _PAPER):
            return True
        # Paper beats rock
        if (self.move == _PAPER and ac2.move == _ROCK):
            return True
        return False

    def __str__(self):
        if self.move == _ROCK:
            return 'Rock'
        if self.move == _SCISSOR:
            return 'Scissors'
        return 'Paper'

    def __int__(self):
        return self.move


class SingleGame():
    '''
    Play a single game of RPS with two players
    '''

    def __init__(self, p_1, p_2):
        self.p_1 = p_1
        self.p_2 = p_2
        self.p_1_move = None
        self.p_2_move = None
        self.winner = None

    def __str__(self):
        wname = self.winner.get_name() if self.winner else 'None'
        return ('{}: '.format(self.p_1.get_name()) +
                '{}'.format(str(self.p_1_move).ljust(12)) +
                '{}: '.format(self.p_2.get_name()) +
                '{}'.format(str(self.p_2_move).ljust(12)) +
                '-> Winner: {}\n'.format(wname))

    def play(self):
        ''' Get each players move, find the winner and report back '''
        self.p_1_move = self.p_1.choose_action()
        self.p_2_move = self.p_2.choose_action()
        self.winner = self.get_winner(self.p_1_move, self.p_2_move)

        # Tie
        if self.winner is None:
            self.p_1.get_result(self.p_2_move, winner=None)
            self.p_2.get_result(self.p_1_move, winner=None)

        # Player 1 won
        elif self.winner is self.p_1:
            self.p_1.get_result(self.p_2_move, winner=1)
            self.p_2.get_result(self.p_1_move, winner=0)

        # Player 2 won
        elif self.winner is self.p_2:
            self.p_1.get_result(self.p_2_move, winner=0)
            self.p_2.get_result(self.p_1_move, winner=1)

    def get_winner(self, player1_move, player2_move):
        ''' Return the winner, None if it is a tie '''
        if player1_move == player2_move:
            return None
        if player1_move > player2_move:
            return self.p_1
        return self.p_2


class MultipleGames():
    '''
    Class to represent multiple games
    '''

    def __init__(self, p1=None, p_2=None, **kwargs):
        self.p_1 = p1
        self.p_2 = p_2
        self.num_games = kwargs.get('num_games', 100)
        self.print_games = kwargs.get('print_games', False)
        self.plot_games = kwargs.get('plot', False)

    def arrange_single_game(self):
        ''' Arrange a single game '''
        game = SingleGame(self.p_1, self.p_2)
        game.play()
        if self.print_games:
            print(game)

    def arrange_tournament(self):
        ''' Arrange a tournament with num_games rounds '''
        averages = []
        for i in range(1, self.num_games+1):
            self.arrange_single_game()
            curr_average = self.p_1.get_score() / i
            averages += [curr_average]

        if self.plot_games:
            self.plot_game(averages)

        if self.print_games:
            print("Total points:")
            print("{}: {}".format(self.p_1.get_name().rjust(25),
                                  self.p_1.score))
            print("{}: {}".format(self.p_2.get_name().rjust(25),
                                  self.p_2.score))
        self.p_1.reset()
        self.p_2.reset()

    def plot_game(self, averages):
        ''' Plot the game '''
        plt.plot(list(range(self.num_games)), averages)
        plt.title('{} vs. {}'.format(self.p_1.get_name(), self.p_2.get_name()))
        plt.xlabel('Game number')
        plt.ylabel('Average score for {}'.format(self.p_1.get_name()))
        plt.ylim((0, 1))
        plt.axhline(y=0.5, linestyle='dotted', color='black')
        plt.grid()
        plt.show()


def usage():
    '''
    Print usage
    '''
    return '''Usage: python {0} [OPTS] "<P1>" "<P2>"
Options:
        -n <num_games> :  Play <num_games> rounds. Defaults to 100
        -p             :  Print each round
        -P             :  Plot P1's average score against P2
        -h             :  Print help (this)

If P1 and P2 are not supplied, P1 defaults to Hist(2), and P2 defaults to Seq.
P1 and P2 can be any of the following:

        Rand           :  Choose a random move each time
        Seq            :  Choose move sequentially; R, P, S, R, P, S, ...
        Hist(<number>) :  Keep a history, search, optimize
        Freq           :  Counter opponents most frequent move
        OTP            :  One Trick Pony, choose one move, stick to it

For example, to simulate a 100 round tournament between Seq and Freq, both
printed and plotted:

        python {0} -pP -n 100 "Freq" "Seq"
    '''.format(os.path.basename(__file__))


def main():
    """
    Play RPS
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:pPh", [
            "numgames=", "print", "plot", "help"
        ])
    except getopt.GetoptError as err:
        print(str(err))
        print(usage())
        sys.exit(2)

    ngames = 100
    printg = False
    plot = False
    for opt, arg in opts:
        if opt in ("-n", "--numgames"):
            ngames = int(arg)
        elif opt in ("-p", "--print"):
            printg = True
        elif opt in ("-P", "--plot"):
            plot = True
        elif opt in ("-h", "--help"):
            print(usage())
            sys.exit(0)

    if len(args) == 2:
        p1_pstyle, p1_hsize = ap.parse_args(args[0])
        p2_pstyle, p2_hsize = ap.parse_args(args[1])

        p_1 = Player(play_style=p1_pstyle, hist=p1_hsize)
        p_2 = Player(play_style=p2_pstyle, hist=p2_hsize)
    else:
        p_1 = Player(play_style=_HIST, hist=2)
        p_2 = Player(play_style=_SEQ)

    games = MultipleGames(p_1, p_2,
                          num_games=ngames,
                          print_games=printg,
                          plot=plot)

    games.arrange_tournament()


if __name__ == '__main__':
    main()
