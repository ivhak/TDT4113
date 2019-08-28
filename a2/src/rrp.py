import random
import matplotlib.pyplot as plt

_ROCK = 0
_SCISSOR = 1
_PAPER = 2

_RAND = 0
_SEQ = 1
_HIST = 2
_FREQ = 3


class player():
    def __init__(self, play_style=0, hist=0):

        # Choose a class to make action choices
        if play_style == _RAND:
            self.player_style = rand()

        elif play_style == _SEQ:
            self.player_style = seq()

        elif play_style == _HIST:
            self.player_style = history(hist_size=hist)

        elif play_style == _FREQ:
            self.player_style = freq()

        self.score = 0

    def get_result(self, my_move=None, opp_move=None, winner=None):

        # If the player_style is history or freq, update the list of the
        # oppenents moves
        if (isinstance(self.player_style, history)
                or isinstance(self.player_style, freq)):
            self.player_style.add_opp_move(int(opp_move))

        if winner is None:
            self.score += 0.5     # tie
        else:
            self.score += winner  # win = 1, lose = 0

    def get_name(self):
        return self.player_style.get_name()

    def choose_action(self):
        move = self.player_style.make_move()
        return action(move)

    def get_score(self):
        return self.score

    def reset(self):
        self.score = 0
        self.player_style.reset()


class rand():
    def make_move(self):
        return random.randint(0, 2)

    def get_name(self):
        return "Random"

    def reset(self):
        return


class seq():
    def __init__(self):
        self.loop_count = 0

    def make_move(self):
        self.loop_count = (self.loop_count + 1) % 3
        return self.loop_count

    def get_name(self):
        return "Sequential"

    def reset(self):
        self.loop_count = 0


class freq():
    def __init__(self):
        self.move_count = [0, 0, 0]

    def make_move(self):
        if self.move_count == [0, 0, 0]:
            return random.randint(0, 2)

        return (self.move_count.index(max(self.move_count)) + 1) % 3

    def add_opp_move(self, opp_move):
        self.move_count[int(opp_move)] += 1

    def get_name(self):
        return "Frequency"

    def reset(self):
        self.move_count = [0, 0, 0]


class history():
    def __init__(self, hist_size=0):
        self.opp_hist = []
        self.hist_size = hist_size

    def make_move(self):
        if len(self.opp_hist) < self.hist_size + 1:
            # History is not big enough yet, choose a random move
            return random.randint(0, 2)

        else:
            # Get the <hist_size> last moves done by the opponent
            last_moves = self.opp_hist[len(self.opp_hist) - self.hist_size:]

            # Count of how many times the moves came after these last moves
            # previously
            move_count = [0, 0, 0]

            # Loop through the history to find slices equal to <last_moves>
            for i in range(len(self.opp_hist) - self.hist_size - 1):
                if self.opp_hist[i:i+self.hist_size] == last_moves:
                    next_move = self.opp_hist[i+self.hist_size+1]
                    move_count[next_move] += 1

            # The index of the max value in move_count will be the move most
            # often done after the last_moves -> return the move that beats
            # this move:
            return (move_count.index(max(move_count)) + 1) % 3

    def add_opp_move(self, opp_move):
        self.opp_hist += [opp_move]

    def get_name(self):
        return "Historical({})".format(self.hist_size)

    def reset(self):
        self.opp_hist = []


class action():
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
            return "Rock"
        elif self.move == _SCISSOR:
            return "Scissors"
        else:
            return "Paper"

    def __int__(self):
        return self.move


class single_game():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.p1_move = None
        self.p2_move = None
        self.winner = None

    def play(self):
        self.p1_move = self.p1.choose_action()
        self.p2_move = self.p2.choose_action()
        self.winner = self.get_winner(self.p1_move, self.p2_move)

        # Tie
        if self.winner is None:
            self.p1.get_result(self.p1_move, self.p2_move, winner=None)
            self.p2.get_result(self.p2_move, self.p1_move, winner=None)

        # Player 1 won
        elif self.winner is p1:
            self.p1.get_result(self.p1_move, self.p2_move, winner=1)
            self.p2.get_result(self.p2_move, self.p1_move, winner=0)

        # Player 2 won
        elif self.winner is p2:
            self.p1.get_result(self.p1_move, self.p2_move, winner=0)
            self.p2.get_result(self.p2_move, self.p1_move, winner=1)

    def get_winner(self, player1_move, player2_move):
        if player1_move == player2_move:
            return None
        elif player1_move > player2_move:
            return self.p1
        return self.p2

    def __str__(self):
        wname = self.winner.get_name() if self.winner is not None else "None"
        return ('{}: '.format(self.p1.get_name()) +
                '{}, '.format(str(self.p1_move).ljust(12)) +
                '{}: '.format(self.p2.get_name()) +
                '{}, '.format(str(self.p2_move).ljust(12)) +
                '-> Winner: {}\n'.format(wname))


class multiple_games():
    def __init__(self, p1=None, p2=None, num_games=1):
        self.p1 = p1
        self.p2 = p2
        self.num_games = num_games

    def arrange_single_game(self):
        game = single_game(p1, p2)
        game.play()

    def arrange_tournament(self):
        averages = []
        for i in range(1, self.num_games+1):
            self.arrange_single_game()
            curr_average = self.p1.get_score() / i
            averages += [curr_average]

        self.plot_game(averages)

    def plot_game(self, averages):
        plt.plot(list(range(self.num_games)), averages)
        plt.title('{} vs. {}'.format(self.p1.get_name(), self.p2.get_name()))
        plt.xlabel('Game number')
        plt.ylabel('Average score for {}'.format(self.p1.get_name()))
        plt.ylim((0, 1))
        plt.axhline(y=0.5, linestyle='dotted', color='black')
        plt.grid()
        plt.show()
        self.p1.reset()
        self.p2.reset()


if __name__ == '__main__':
    p1 = player(play_style=_HIST, hist=2)
    p2 = player(play_style=_SEQ)
    games = multiple_games(p1, p2, num_games=100)
    games.arrange_tournament()
