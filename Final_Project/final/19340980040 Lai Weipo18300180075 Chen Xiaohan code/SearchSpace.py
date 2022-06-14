import pisqpipe as pp
import itertools

# find possible positions to take move
def Heur_position(board):
    probable_list = []
    scale = 1
    for (pos_x, pos_y) in itertools.product(range(pp.width), range(pp.height)):
        if not board[pos_x][pos_y] == 0:
            continue
        for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
            x, y = pos_x + i - scale, pos_y + j - scale
            if x < 0 or x >= pp.width or y < 0 or y >= pp.height:
                continue
            if not board[x][y] == 0:
                if (pos_x, pos_y) not in probable_list:
                    probable_list.append((pos_x, pos_y))
    if probable_list == []:
        return None
    return probable_list


def update_Heur_position(action, probable_list):
    x, y = action[0], action[1]
    scale = 1
    for (i, j) in itertools.product(range(2 * scale + 1), range(2 * scale + 1)):
        new_x = x + i - scale
        new_y = y + j - scale
        if (new_x, new_y) not in probable_list:
            probable_list.append((new_x, new_y))

    if (x, y) in probable_list:
        probable_list.remove((x, y))
    return probable_list