from SearchSpace import Heur_position
import algorithms
import pisqpipe as pp

import re
from collections import Counter
import itertools
pattern_dict = {("C5", (), ()): "11111",
                ("H4", (0, 5), ()): "011110",
                ("C4", (0), (5)): "011112",
                ("C4", (5), (0)): "211110",
                ("C4", (0, 2, 6), ()): "0101110",
                ("C4", (0, 4, 6), ()): "0111010",
                ("C4", (0, 3, 6), ()): "0110110",#開始添加
                ("C4", (0, 3), (6)): "0110112",
                ("C4", (1), (5)): "101112",
                ("C4", (2), (5)): "110112",
                ("C4", (3), (5)): "111012",
                ("C4", (4), (5)): "111102",
                ("C4", (4), (0)): "211101",
                ("C4", (3), (0)): "211011",
                ("C4", (3, 6), (0)): "2110110",
                ("C4", (2), (0)): "210111",
                ("C4", (1), (0)): "201111",
                ("S4", (), (0, 5)): "211112",
                ("S3", (), (0, 4)): "21112",
                ("S2", (), (0, 3)): "2112",#stop
                ("H3", (0, 4), ()): "01110",
                ("H3", (0, 2, 5), ()): "010110",
                ("H3", (0, 3, 5), ()): "011010",
                ("M3", (0, 1), (5)): "001112",
                ("M3", (4, 5), (0)): "211100",
                ("M3", (0, 2), (5)): "010112",
                ("M3", (3, 5), (0)): "211010",
                ("M3", (0, 3), (5)): "011012",
                ("M3", (2, 5), (0)): "210110",
                ("M3", (1, 2), ()): "10011",
                ("M3", (2, 3), ()): "11001",
                ("M3", (1, 3), ()): "10101",
                ("M3", (1, 4), (0, 6)): "2011102",
                ("H2", (0, 1, 4), ()): "00110",
                ("H2", (0, 3, 4), ()): "01100",
                ("H2", (0, 2, 4), ()): "01010",
                ("H2", (0, 2, 3, 5), ()): "010010",
                ("M2", (0, 1, 2), (5)): "000112",
                ("M2", (3, 4, 5), (0)): "211000",
                ("M2", (0, 1, 3), (5)): "001012",
                ("M2", (2, 4, 5), (0)): "210100",
                ("M2", (0, 2, 3), (5)): "010012",
                ("M2", (2, 3, 5), (0)): "210010",
                ("M2", (1, 2, 3), ()): "10001",
                ("M2", (1, 3, 5), (0, 6)): "2010102",
                ("M2", (1, 4, 5), (0, 6)): "2011002",
                ("M2", (1, 2, 5), (0, 6)): "2001102"
                }
score_dict = {"C5": 2000000,
              "H4": 10000,
              "C4": 1000,
              "H3": 200,
              "M3": 50,
              "H2": 5,
              "M2": 3,
              "S4": -5,
              "S3": -5,
              "S2": -5,
              # scores of combination of patterns
              "C4C4": 11000,
              "C4H3": 9000,
              "H3H3": 6000,
              "H3M3": 1000,
              "H3H2": 700,
              "H2H2H2": 300,
              "H2H2": 100,
              "H2M2": 10

              }
def get_class(board, position):
    current_class = []
    width, height = len(board), len(board[0])

    # horizontal
    hori_list = []
    if position[0] < 4:
        for i in range(position[0] + 5):
            hori_list.append(str(board[i][position[1]]))
    elif position[0] > width - 5:
        for i in range(position[0] - 4, width):
            hori_list.append(str(board[i][position[1]]))
    else:
        for i in range(position[0] - 4, position[0] + 5):
            hori_list.append(str(board[i][position[1]]))
    hori_str = "".join(hori_list)
    for type in pattern_dict.keys():
        if type in hori_str:
            current_class.append(current_class[type])
            break

    #vertical
    vert_list = []
    if position[1] < 4:
        for i in range(position[1] + 5):
            vert_list.append(str(board[position[0]][i]))
    elif position[1] > height - 5:
        for i in range(position[1] - 4, height):
            vert_list.append(str(board[position[0]][i]))
    else:
        for i in range(position[1] - 4, position[1] + 5):
            vert_list.append(str(board[position[0]][i]))
    vert_str = "".join(vert_list)
    for type in pattern_dict.keys():
        if type in vert_str:
            current_class.append(current_class[type])
            break

    #diagonal
    diag_list = []
    diff = position[0] - position[1]
    if position[1] < 4:
        if position[0] < position[1]:
            for i in range(position[0] + 5):
                diag_list.append(str(board[i][i - diff]))
        elif position[0] > width - 5:
            for i in range(width - position[0] + position[1]):
                diag_list.append(str(board[diff + i][i]))
        else:
            for i in range(position[1] + 5):
                diag_list.append(str(board[diff + i][i]))
    elif position[1] > height - 5:
        if position[0] > position[1]:
            for i in range(position[0] - 4, width):
                diag_list.append(str(board[i][i - diff]))
        elif position[0] < 4:
            for i in range(height + diff):
                diag_list.append(str(board[i][i - diff]))
        else:
            for i in range(position[1] - 4, height):
                diag_list.append(str(board[i + diff][i]))
    else:
        if position[0] < 4:
            for i in range(position[0] + 5):
                diag_list.append(str(board[i][i - diff]))
        elif position[0] > width - 5:
            for i in range(position[0] - 4, width):
                diag_list.append(str(board[i][i - diff]))
        else:
            for i in range(position[0] - 4, position[0] + 5):
                diag_list.append(str(board[i][i - diff]))
    diag_str = "".join(diag_list)
    for type in pattern_dict.keys():
        if type in diag_str:
            current_class.append(pattern_dict[type])
            break

    #Back diagonal
    bdiag_list = []
    sum = position[0] + position[1]
    if position[1] < 4:
        if position[0] < 4:
            for i in range(sum + 1):
                bdiag_list.append(str(board[i][sum - i]))
        elif position[0] >= width - position[1]:
            for i in range(position[0] - 4, width):
                bdiag_list.append(str(board[i][sum - i]))
        else:
            for i in range(position[1] + 5):
                bdiag_list.append(str(board[sum - i][i]))
    elif position[1] > height - 5:
        if position[0] > width - 5:
            for i in range(sum - height + 1, height):
                bdiag_list.append(str(board[i][sum - i]))
        elif sum < width:
            for i in range(position[0] + 5):
                bdiag_list.append(str(board[i][sum - i]))
        else:
            for i in range(position[1] - 4, height):
                bdiag_list.append(str(board[sum - i][i]))
    else:
        if position[0] < 4:
            for i in range(position[0] + 5):
                bdiag_list.append(str(board[i][sum - i]))
        elif position[0] > width - 5:
            for i in range(position[0] - 4, width):
                bdiag_list.append(str(board[i][sum - i]))
        else:
            for i in range(position[0] - 4, position[0] + 5):
                bdiag_list.append(str(board[i][sum - i]))
    bdiag_str = "".join(bdiag_list)

    for type in pattern_dict.keys():
        if type in bdiag_str:
            current_class.append(pattern_dict[type])
            break

    return current_class


def position_score(board, position):
    width, height = len(board), len(board[0])
    return max(min(position[0], width - position[0]), min(position[1], height - position[1]))


def change_color(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            matrix[i][j] = (3 - matrix[i][j]) % 3
    return matrix


def move_attack_evaluate(board, position, color):
    temp_board = [[board[x][y] for y in range(20)] for x in range(20)]
    if color == 2:
        temp_board = change_color(temp_board)

    temp_board[position[0]][position[1]] = 1
    current_class = get_class(temp_board, position)
    if current_class:
        temp_str = "".join(current_class)
        counter = Counter()
        score = 0

        for class_name in score_dict.values():
            counter[class_name] = len(re.findall(class_name, temp_str))
        for class_name in counter.keys():
            score = max(score, score_dict[class_name] * counter[class_name])
        if counter["C4"] >= 2:
            score = max(score, score_dict["C4C4"])
        elif counter["C4"] * counter["H3"]:
            score = max(score, score_dict["C4H3"])
        elif counter["H3"] >= 2:
            score = max(score, score_dict["H3H3"])
        elif counter["H3"] * counter["M3"]:
            score = max(score, score_dict["H3M3"])
        elif counter["H3"] * counter["H2"]:
            score = max(score, score_dict["H3H2"])
        elif counter["H2"] >= 3:
            score = max(score, score_dict["H2H2H2"])
        elif counter["H2"] >= 2:
            score = max(score, score_dict["H2H2"])
        elif counter["H2"] * counter["M2"]:
            score = max(score, score_dict["H2M2"])
        return score
    else:
        return 0


# evaluate the score of the move
def move_evaluate(board, position):
    off_score = move_attack_evaluate(board, position, 1)
    def_score = move_attack_evaluate(board, position, 2)
    pos_score = position_score(board, position)
    score = off_score + def_score + pos_score
    return score


# evaluate the score of current board
def board_evaluate(board):
    evaluation = []
    for next_position in Heur_position(board):
        evaluation.append((move_evaluate(board, next_position), next_position))
    return evaluation


def get_class_2(board, position, record, counter):
    # 用当前位置各棋型的数量更新counter
    cur_class = []
    # 横向
    if record[position[0]][position[1]][0] == 0:
        hori_list = []
        for i in range(-4, 5):
            if position[0] + i < 0 or position[0] + i >= pp.width:
                hori_list.append("2")
            else:
                hori_list.append(str(board[position[0] + i][position[1]]))
        hori_str = "".join(hori_list)
        for type in pattern_dict.keys():
            if type in hori_str:
                cur_class.append(pattern_dict[type])
                for temp in range(5):
                    if position[0] + temp < pp.width:
                        if board[position[0] + temp][position[1]] == 2:
                            break
                        record[position[0] + temp][position[1]][0] = 1
                    else:
                        break
                for temp in range(-1, -5, -1):
                    if position[0] + temp >= 0:
                        if board[position[0] + temp][position[1]] == 2:
                            break
                        record[position[0] + temp][position[1]][0] = 1
                    else:
                        break
                break

    # 纵向
    if record[position[0]][position[1]][1] == 0:
        vert_list = []
        for i in range(-4, 5):
            if position[1] + i < 0 or position[1] + i >= pp.height:
                vert_list.append("2")
            else:
                vert_list.append(str(board[position[0]][position[1] + i]))
        vert_str = "".join(vert_list)
        for type in pattern_dict.keys():
            if type in vert_str:
                cur_class.append(pattern_dict[type])
                for temp in range(5):
                    if position[1] + temp < pp.height:
                        if board[position[0]][position[1] + temp] == 2:
                            break
                        record[position[0]][position[1] + temp][1] = 1
                    else:
                        break
                for temp in range(-1, -5, -1):
                    if position[0] + temp >= 0:
                        if board[position[0]][position[1] + temp] == 2:
                            break
                        record[position[0]][position[1] + temp][1] = 1
                    else:
                        break
                break

    # 主对角
    if record[position[0]][position[1]][2] == 0:
        diag_list = []
        for i in range(-4, 5):
            if position[0] + i < 0 or position[0] + i >= pp.width or position[1] + i < 0 or\
                    position[1] + i >= pp.height:
                diag_list.append("2")
            else:
                diag_list.append(str(board[position[0] + i][position[1] + i]))
        diag_str = "".join(diag_list)
        for type in pattern_dict.keys():
            if type in diag_str:
                cur_class.append(pattern_dict[type])
                for temp in range(5):
                    if position[1] + temp < pp.height and position[0] + temp < pp.width:
                        if board[position[0] + temp][position[1] + temp] == 2:
                            break
                        record[position[0] + temp][position[1] + temp][2] = 1
                    else:
                        break
                for temp in range(-1, -5, -1):
                    if position[0] + temp >= 0 and position[1] + temp >= 0:
                        if board[position[0] + temp][position[1] + temp] == 2:
                            break
                        record[position[0] + temp][position[1] + temp][2] = 1
                    else:
                        break
                break

    # 反对角
    if record[position[0]][position[1]][3] == 0:
        bdiag_list = []
        for i in range(-4, 5):
            if position[0] + i < 0 or position[0] + i >= pp.width or position[1] - i < 0 or position[
                1] - i >= pp.height:
                bdiag_list.append("2")
            else:
                bdiag_list.append(str(board[position[0] + i][position[1] - i]))
        bdiag_str = "".join(bdiag_list)

        for type in pattern_dict.keys():
            if type in bdiag_str:
                cur_class.append(pattern_dict[type])
                for temp in range(5):
                    if position[0] + temp < pp.width and position[1] - temp >= 0:
                        if board[position[0] + temp][position[1] - temp] == 2:
                            break
                        record[position[0] + temp][position[1] - temp][3] = 1
                    else:
                        break
                for temp in range(-1, -5, -1):
                    if position[0] + temp >= 0 and position[1] - temp < pp.height:
                        if board[position[0] + temp][position[1] - temp] == 2:
                            break
                        record[position[0] + temp][position[1] - temp][3] = 1
                    else:
                        break
                break

    if cur_class:
        temp_str = "".join(cur_class)
        temp_counter = Counter()
        for type in pattern_dict.values():
            temp_counter[type] = len(re.findall(type, temp_str))
        temp_items = list(score_dict.keys())[0:11]
        if temp_counter["C4"] >= 2:
            counter["C4C4"] += 1
            temp_items.remove("C4")
        elif temp_counter["C4"] * temp_counter["H3"]:
            counter["C4H3"] += 1
            temp_items.remove("H3")
            temp_items.remove("C4")
        elif temp_counter["H3"] >= 2:
            counter["H3H3"] += 1
            temp_items.remove("H3")
        elif temp_counter["H3"] * temp_counter["M3"]:
            counter["H3M3"] += 1
            temp_items.remove("H3")
            temp_items.remove("M3")
        elif temp_counter["H3"] * temp_counter["H2"]:
            counter["H3H2"] += 1
            temp_items.remove("H3")
            temp_items.remove("H2")
        elif temp_counter["H2"] >= 3:
            counter["H2H2H2"] += 1
            temp_items.remove("H2")
        # elif temp_counter["M3"] * temp_counter["H2"]:
        #     counter["M3H2"] += 1
        #     temp_items.remove("M3")
        #     temp_items.remove("H2")
        elif temp_counter["H2"] >= 2:
            counter["H2H2"] += 1
            temp_items.remove("H2")
        elif temp_counter["H2"] * temp_counter["M2"]:
            counter["H2M2"] += 1
            temp_items.remove("H2")
            temp_items.remove("M2")
        for type in temp_items:
            counter[type] += temp_counter[type]


def get_all_types(board):
    record = [[[0, 0, 0, 0] for x in range(pp.width)] for y in range(pp.height)]
    counter = Counter()
    for type in score_dict.keys():
        counter[type] = 0
    for i in range(pp.width):
        for j in range(pp.height):
            if board[i][j] != 0:
                get_class_2(board, (i, j), record, counter)
    return counter


def is_win(board):
    counter = get_all_types(board)
    if counter["C4"] > 0 or counter["H4"] > 0 or counter["C4H3"] > 0 or counter["C4C4"] > 0:
        return True
    else:
        return False


def is_dangerous(board):
    # 危险评估函数，更提前和准确，但更消耗算力
    temp_board = [[(3 - board[i][j]) % 3 for j in range(pp.height)] for i in range(pp.width)]
    for position in Heur_position(board):
        temp_board[position[0]][position[1]] = 1
        counter = get_all_types(temp_board)
        if counter["C5"] > 0 or counter["H4"] > 0 or counter["C4"] > 0 or counter["H3"] > 0 or counter["S4"] > 0 \
                or counter["C4C4"] > 0 or counter["C4H3"] > 0 or counter["H3H3"] > 0:
            return True
        temp_board[position[0]][position[1]] = 0
    return False


# defense函数
def defense(board):
    temp_board = [[(3 - board[i][j]) % 3 for j in range(pp.height)] for i in range(pp.width)]
    defense_dict = {}
    for position in Heur_position(board):
        temp_board[position[0]][position[1]] = 1
        counter = get_all_types(temp_board)
        if counter["C5"] > 0 or counter["H4"] > 0 \
                or counter["C4C4"] > 0 or counter["C4H3"] > 0 or counter["H3H3"] > 0:
            defense_dict[position] = counter["C5"] + 0.8 * counter["H4"] \
                                     + 0.7 * counter["C4C4"] + 0.6 * counter["C4H3"] + 0.5 * counter["H3H3"]
        temp_board[position[0]][position[1]] = 0
    if not bool(defense_dict):
        return None
    else:
        return max(defense_dict, key=defense_dict.get)


def find_C5(board):
    record = [[[0, 0, 0, 0] for x in range(pp.width)] for y in range(pp.height)]
    counter = Counter()
    tempx, tempy = -1, -1
    for type in score_dict.keys():
        counter[type] = 0
    for i, j in itertools.product(range(pp.width), range(pp.height)):
        if board[i][j] != 0:
            get_class_2(board, (i, j), record, counter)
            if counter["C4"] > 0 or counter["H4"] > 0 or counter["C4H3"] > 0 or counter["C4C4"] > 0 or counter[
                "H3H3"] > 0:
                tempx, tempy = i, j
                break
    temp_counter = Counter()
    for type in score_dict.keys():
        temp_counter[type] = 0
    for x, y in itertools.product(range(-4, 5), range(-4, 5)):
        if 0 <= x + tempx < pp.width and 0 <= y + tempy < pp.height:
            if board[x + tempx][y + tempy] == 0:
                board[x + tempx][y + tempy] = 1
                temp_record = [[[0, 0, 0, 0] for a in range(pp.width)] for b in range(pp.height)]
                get_class_2(board, (x + tempx, y + tempy), temp_record, temp_counter)
                board[x + tempx][y + tempy] = 0
                if temp_counter["C5"] or temp_counter["H4"]:
                    return x + tempx, y + tempy
    return None