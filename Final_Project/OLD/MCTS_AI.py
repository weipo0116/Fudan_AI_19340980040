# -*- coding = utf-8 -*-
# @Time : 2021/1/12 10:21
# @Author : 詹远瞩, 陈劭涵
# @File : MCTS_AI.py
# @Software : PyCharm

# This file is the implementation of MCTS algorithm

import pisqpipe as pp
from pisqpipe import DEBUG_EVAL, DEBUG
from Evaluate import *

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 20
board = [[0 for i in range(MAX_BOARD)] for j in range(MAX_BOARD)]
moves = []
players = []

def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            board[x][y] = 0
    pp.pipeOut("OK")


def isFree(x, y):
    return x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] == 0


def brain_my(x, y):
    if isFree(x, y):
        board[x][y] = 1
        moves.append((x,y))
        players.append(1)
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    if isFree(x, y):
        board[x][y] = 2
        moves.append((x, y))
        players.append(2)
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_block(x, y):
    if isFree(x, y):
        board[x][y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
    if x >= 0 and y >= 0 and x < pp.width and y < pp.height and board[x][y] != 0:
        board[x][y] = 0
        return 0
    return 2


def is_terminal(board):
    if is_win(board):
        return True, 1
    else:
        new_board = change_color(board)
        if is_win(new_board):
            return True, 2
        else:
            return False, None


class MCTS(object):
    def __init__(self, board, player, max_times=2000):
        self.player = player
        self.board = board
        self.time_limit = 13
        self.max_times = max_times
        self.c = 1.44
        self.breath = 5
        self.simu = 0

        self.simu_times = {}
        self.win_times = {}

    def get_ucb(self, positions):
        from math import log, sqrt
        max_value = float('-inf')
        max_move = None
        for move in positions:
            value = self.win_times[(self.player, move)] / self.simu_times[(self.player, move)] + \
                    self.c * sqrt(log(self.simu) / self.simu_times[(self.player, move)])
            if value > max_value:
                max_value = value
                max_move = move
        return max_value, max_move

    def get_possible_position(self, player):
        raw = Heur_position(self.board)
        positions = []
        ranking_list = []
        if len(raw) > self.breath:
            for option in raw:
                board[option[0]][option[1]] = player
                v = board_evaluate(board)
                board[option[0]][option[1]] = 0
                ranking_list.append(v)
            temp = [v for v in ranking_list]
            temp.sort(reverse=True)
            for v in temp[0:self.breath]:
                option = raw[ranking_list.index(v)]
                positions.append(option)
            return positions
        else:
            return raw

    def MCTS_proc(self, temp_board, temp_moves, temp_players):
        from random import choice
        if players[-1] == 2:
            player = 1
        else:
            player = 2
        possible_position = self.get_possible_position(player)

        visited = set()
        winner = -1
        expand = True
        i = 0
        while i < self.max_times:
            if all(self.simu_times.get((player, move)) for move in possible_position):
                value, move = self.get_ucb(possible_position)

            else:
                move = choice(possible_position)

            temp_board[move[0]][move[1]] = player
            temp_moves.append(move)
            temp_players.append(player)
            possible_position.remove(move)

            if expand is True and (player, move) not in self.simu_times:
                expand = False
                self.simu_times[(player, move)] = 0
                self.win_times[(player, move)] = 0

            visited.add((player, move))
            terminal, winner = is_terminal(temp_board)
            if terminal or not len(possible_position):
                break

            if players[-1] == 2:
                player = 1
            else:
                player = 2

        for (player, move) in visited:
            if (player, move) in self.simu_times:
                self.simu_times[(player, move)] += 1
                self.simu += 1
                if player == winner:
                    self.win_times[(player, move)] += 1

    def return_action(self):
        from copy import deepcopy
        from random import choice
        import time
        start_time = time.time()
        while time.time() - start_time < self.time_limit:
            temp_board = deepcopy(self.board)
            temp_moves = deepcopy(moves)
            temp_players = deepcopy(players)
            self.MCTS_proc(temp_board, temp_moves, temp_players)
        best_move = choice(self.get_possible_position(self.player))
        best_score = 0
        for move in self.get_possible_position(self.player):
            score = self.win_times[(self.player, move)]/self.simu_times[(self.player, move)]
            if score > best_score:
                best_move = move
        return best_move

def brain_turn():
    # try:
    #     logDebug("now debug")
    if pp.terminateAI:
        return
    x, y = -1, -1
    if is_win(board):
        (x, y) = find_C5(board)
    else:
        # op_board = [[(3 - board[i][j]) % 3 for j in range(pp.height)] for i in range(pp.width)]
        if is_dangerous(board):
            result = defense(board)
            if result is not None:
                x, y = result[0], result[1]
            else:
                if not moves:
                    x, y = (10, 10)
                else:
                    Agent = MCTS(board, 1, 10000)
                    x, y = Agent.return_action()
        else:
            if not moves:
                x, y = (10, 10)
            else:
                Agent = MCTS(board, 1, 10000)
                x, y = Agent.return_action()
    pp.do_mymove(x, y)
    #     logDebug("turn ends")
    # except:
    #     logTraceBack()

def brain_end():
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


if DEBUG_EVAL:
    import win32gui


    def brain_eval(x, y):
        # TODO check if it works as expected
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(board[x][y])
        win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)
"""
######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing "")
######################################################################
# define a file for logging ...
DEBUG_LOGFILE = "D:/mcts/pbrain-mcts.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
    pass

# define a function for writing messages to the file
def logDebug(msg):
    with open(DEBUG_LOGFILE,"a") as f:
        f.write(msg+"\n")
        f.flush()

# define a function to get exception traceback
def logTraceBack():
    import traceback
    with open(DEBUG_LOGFILE,"a") as f:
        traceback.print_exc(file=f)
        f.flush()
    raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
# def brain_turn():
# 	logDebug("some message 1")
# 	try:
# 		logDebug("some message 2")
# 		# some code raising an exception
# 		logDebug("some message 3") # not logged, as it is after error
# 	except:
# 		logTraceBack()

######################################################################
"""
# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
    pp.brain_eval = brain_eval


def main():
    pp.main()


if __name__ == "__main__":
    main()
