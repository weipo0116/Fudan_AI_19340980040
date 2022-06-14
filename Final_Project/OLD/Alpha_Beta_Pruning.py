# -*- coding = utf-8 -*-
# @Time : 2020/12/4 19:26
# @Author : 陈劭涵, 詹远瞩
# @File : Alpha_Beta_Pruning.py
# @Software : PyCharm

# This file is implementation of the alpha-beta pruning algorithm

import Role as role_def
from Evaluate import *
from SearchSpace import *

class Node:
    def __init__(self, player=role_def.ME, successor=None, isLeaf=False, value=None, action=None):
        if successor is None:
            successor = []
        if player == role_def.ME:
            self.rule = 'max'
        if player == role_def.OP:
            self.rule = 'min'
        self.successor = successor
        self.isLeaf = isLeaf
        self.value = value
        self.action = action


def GetValue(node, alpha, beta):
    if node.rule == 'max':
        return MaxValue(node, alpha, beta)
    else:
        return MinValue(node, alpha, beta)


def MaxValue(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    else:
        action = None
        v = alpha
        upper_bound = float('-inf')
        for successor in node.successor:
            if MinValue(successor, v, beta)[0] > upper_bound:
                upper_bound = MinValue(successor, v, beta)[0]
                action = successor.action
            if upper_bound >= beta:
                return upper_bound, None
            v = max(v, upper_bound)
        return upper_bound, action


def MinValue(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    else:
        action = None
        v = beta
        lower_bound = float('inf')
        for successor in node.successor:
            if MaxValue(successor, alpha, v)[0] < lower_bound:
                action = successor.action
                lower_bound = MaxValue(successor, alpha, v)[0]
            if lower_bound <= alpha:
                return lower_bound, None
            v = min(lower_bound, v)
        return lower_bound, action


def Construct_tree(n, board, player, action, position_options=None):
    # constraint for search breath
    breadth = 3
    node = Node(player=player, action=action)
    successors = []
    if position_options is None:
        position_options = Heur_position(board)
        if position_options is None:
            return None
    ranking_list = []
    if n == 1:
        if len(position_options) < breadth:
            for option in position_options:
                temp_board = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                # value evaluated by our model
                v = move_evaluate(temp_board, option)
                successors.append(Node(player=3 - player, isLeaf=True, value=v, action=option))
        else:
            for option in position_options:
                temp_board = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                v = move_evaluate(temp_board, option)
                ranking_list.append(v)
            temp_list = ranking_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:breadth]:
                option = position_options[ranking_list.index(v)]
                successors.append(Node(player=3 - player, isLeaf=True, value=v, action=option))
    else:
        if len(position_options) < breadth:
            for option in position_options:
                temp_board = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                successors.append(Construct_tree(n - 1, temp_board, 3 - player, option,
                                                 update_Heur_position(option, position_options)))
        else:
            for option in position_options:
                temp_board = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                ranking_list.append(board_evaluate(temp_board))
            temp_list = ranking_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:breadth]:
                option = position_options[ranking_list.index(v)]
                temp_board = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                successors.append(Construct_tree(n - 1, temp_board, 3 - player, option,
                                                 update_Heur_position(option, position_options)))
    node.successor = successors
    return node



