import pisqpipe as pp
import itertools
from collections import Counter
import re
#import copy

#首先进行棋型拟合、得分计算等算法设计
def detect_pattern(board, player):
    """
    识别棋型，其中包括连五、活四、冲四、活三、眠三、活二和眠二这7种基本棋型，并返回每种棋型的数量
    """
    height, width = len(board), len(board[0])
    if player == 2:
        for i in range(height):
            for j in range(width):
                board[i][j] = (3 - board[i][j]) % 3 #将1和2对换
      #  list_str = board
    pattern_dict = {("Lian Wu", (), ()): "11111",
                    ("Huo Si", (0, 5), ()): "011110",
                    ("Chong Si", (0), (5)): "011112",
                    ("Chong Si", (5), (0)): "211110",
                    ("Chong Si", (0, 2, 6), ()): "0101110",
                    ("Chong Si", (0, 4, 6), ()): "0111010",
                    ("Chong Si", (0, 3, 6), ()): "0110110",
                    ("Huo San", (0, 4), ()): "01110",
                    ("Huo San", (0, 2, 5), ()): "010110",
                    ("Huo San", (0, 3, 5), ()): "011010",
                    ("Mian San", (0, 1), (5)): "001112",
                    ("Mian San", (4, 5), (0)): "211100",
                    ("Mian San", (0, 2), (5)): "010112",
                    ("Mian San", (3, 5), (0)): "211010",
                    ("Mian San", (0, 3), (5)): "011012",
                    ("Mian San", (2, 5), (0)): "210110",
                    ("Mian San", (1, 2), ()): "10011",
                    ("Mian San", (2, 3), ()): "11001",
                    ("Mian San", (1, 3), ()): "10101",
                    ("Mian San", (1, 4), (0, 6)): "2011102",
                    ("Huo Er", (0, 1, 4), ()): "00110",
                    ("Huo Er", (0, 3, 4), ()): "01100",
                    ("Huo Er", (0, 2, 4), ()): "01010",
                    ("Huo Er", (0, 2, 3, 5), ()): "010010",
                    ("Mian Er", (0, 1, 2), (5)): "000112",
                    ("Mian Er", (3, 4, 5), (0)): "211000",
                    ("Mian Er", (0, 1, 3), (5)): "001012",
                    ("Mian Er", (2, 4, 5), (0)): "210100",
                    ("Mian Er", (0, 2, 3), (5)): "010012",
                    ("Mian Er", (2, 3, 5), (0)): "210010",
                    ("Mian Er", (1, 2, 3), ()): "10001",
                    ("Mian Er", (1, 3, 5), (0, 6)): "2010102",
                    ("Mian Er", (1, 4, 5), (0, 6)): "2011002",
                    ("Mian Er", (1, 2, 5), (0, 6)): "2001102"
                    } #棋型字典key为(棋型, 空位坐标, 对手坐标)，后两个元素仅起区分作用
    pattern_counter = Counter()
    #进行方向为(1,0)的行扫描
    for row_index in range(height):
        row = board[row_index]
        row_str = "".join(map(str, row))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], row_str))
    #进行方向为(0,1)的列扫描
    for col_index in range(width):
        col = [a[col_index] for a in board]
        col_str = "".join(map(str, col))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], col_str)) 
    #进行方向为(1,1)的对角线扫描
    for dist in range(0, width+height-1):
        row_ini, col_ini = (dist, 0) if dist < height else (height-1, dist-height+1)
        diag = [board[i][j] for i in range(row_ini, -1, -1) for j in range(col_ini, width) if i + j == dist]
        diag_1_str = "".join(map(str, diag))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], diag_1_str))
    #进行方向为(1,-1)的对角线扫描
    for dist in range(-width+1, height):
        row_ini, col_ini = (0, -dist) if dist < 0 else (dist, 0)
        diag = [board[i][j] for i in range(row_ini, height) for j in range(col_ini, width) if i - j == dist]
        diag_2_str = "".join(map(str, diag))
        for key in pattern_dict:
            pattern_counter[key[0]] += len(re.findall(pattern_dict[key], diag_2_str))    
    return pattern_counter

def pattern_to_score():
    """
    给7种棋型分别赋分
    """
    score_dict = {"Lian Wu": 2000000,
                 "Huo Si": 10000,
                 "Chong Si": 1000,
                 "Huo San": 200,
                 "Mian San": 50,
                 "Huo Er": 5,
                 "Mian Er": 3
                 }
    return score_dict

def board_evaluation(board):
    """
    根据己方与对方棋型计算出当前棋盘总得分，具体地，算法为己方得分减去对方得分*系数(无限制下默认1)
    """
    player_score = 0
    opponent_score = 0
    for pattern, num in detect_pattern(board, 1).items():
        player_score += pattern_to_score()[pattern]*num
    for pattern, num in detect_pattern(board, 2).items():
        if pattern in ['Huo Si', 'Chong Si', 'Lian Wu']: #若对手存在活四、冲四、连五则己方得分大减
            opponent_score += 20*pattern_to_score()[pattern]*num
        elif pattern in ['Huo San']:
            opponent_score += 10*pattern_to_score()[pattern]*num
        else:
            opponent_score += pattern_to_score()[pattern]*num
    score = player_score-opponent_score
    return score

def find_candidate(board):
    """
    寻找下一步可能落子的全部位点
    """
    candidate = []
    scale = 1 #寻找距离现有棋子距离为1的空位
    for (pos_x, pos_y) in itertools.product(range(pp.width), range(pp.height)):
        if not board[pos_x][pos_y] == 0: #跳过点位已有棋子情况
            continue
        for (i,j) in itertools.product(range(2*scale+1), range(2*scale+1)):
            x = pos_x-scale+i
            y = pos_y-scale+j
            if x < 0 or x >= pp.width or y < 0 or y >= pp.height:  
                continue #跳过点位位于棋盘外情况
            if not board[x][y] == 0: 
                candidate.append((pos_x, pos_y))
                break
    if candidate == []:
        return None
    return candidate

def renew_candidate(action, probable_list):
    """
    根据落子位点更新可能落子的位点列表
    """
    x, y = action[0], action[1]
    scale = 1
    for (i, j) in itertools.product(range(2*scale+1), range(2*scale+1)):
        new_x = x-scale+i
        new_y = y-scale+j
        if (new_x, new_y) not in probable_list:
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))
    return probable_list

#其次进行基于Alpha-Beta剪枝的极大极小值搜索算法设计
class Node:
    def __init__(self, player=1, successor=[], isLeaf=False, value=None, action=None):
        if player == 1:
            self.rule = 'max'
        elif player == 2:
            self.rule = 'min'
        self.successor = successor
        self.isLeaf = isLeaf
        self.value = value
        self.action = action

def min_max(node, alpha, beta):
    '''
    极大极小值算法
    '''
    if node.rule == 'max':
        return max_value(node, alpha, beta)
    else:
        return min_value(node, alpha, beta)

def max_value(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    else:
        action = None
        temp_alpha = alpha
        v = float('-inf')
        for child in node.successor:
            if min_value(child, temp_alpha, beta)[0] > v:
                v = min_value(child, temp_alpha, beta)[0] #更新v
                action = child.action
            if v >= beta:
                return v, None #剪枝
            temp_alpha = max(temp_alpha, v) #更新alpha
        return v, action

def min_value(node, alpha, beta):
    if node.isLeaf:
        return node.value, None
    else:
        action = None
        temp_beta = beta
        v = float('inf')
        for child in node.successor:
            if max_value(child, alpha, temp_beta)[0] < v:
                action = child.action
                v = max_value(child, alpha, temp_beta)[0]
            if v <= alpha:
                return v, None
            temp_beta = min(v, temp_beta)
        return v, action

def construct_tree(depth, board, player, action, candidate=None):
    """
    构建搜索树
    """
    thres = 3
    opponent = 3-player
    node = Node(player=player, action=action)
    successors = []
    if candidate == None:
        candidate = find_candidate(board)
        if candidate == None:
            return None
    pref_list = []
    if depth == 1:
        if len(candidate) < thres:
            for pos in candidate:
                board_new = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_new[pos[0]][pos[1]] = player
                temp_value = board_evaluation(board_new)
                successors.append(Node(player=opponent, isLeaf=True, value=temp_value, action=pos))
        else: #若候选位点太多需取能使棋盘得分最高的几个位点
            for pos in candidate:
                board_new = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_new[pos[0]][pos[1]] = player
                temp_value = board_evaluation(board_new)
                pref_list.append(temp_value)
            temp_list = pref_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:thres]:
                pos = candidate[pref_list.index(v)]
                successors.append(Node(player=opponent, isLeaf=True, value=v, action=pos))
    else:
        if len(candidate) < thres:
            for pos in candidate:
                board_new = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_new[pos[0]][pos[1]] = player
                successors.append(construct_tree(depth-1, board_new, opponent, pos, renew_candidate(pos, candidate)))
        else:
            for pos in candidate:
                board_copy = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_copy[pos[0]][pos[1]] = player
                pref_list.append(board_evaluation(board_copy))
            temp_list = pref_list[:]
            temp_list.sort(reverse=True)
            for v in temp_list[0:thres]:
                pos = candidate[pref_list.index(v)]
                board_new = [[board[x][y] for y in range(pp.height)] for x in range(pp.width)]
                board_new[pos[0]][pos[1]] = player
                successors.append(construct_tree(depth-1, board_new, opponent, pos, renew_candidate(pos, candidate)))
    node.successor = successors
    return node    
