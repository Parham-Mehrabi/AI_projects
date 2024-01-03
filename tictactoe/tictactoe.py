"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    # if len(set(block for row in board for block in row)) == 1 and board[0][0] == EMPTY:
    #     return X
    return O if x_count > o_count else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()
    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if col == EMPTY:
                possible_actions.add((i, j))
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board):
        raise ValueError('not a valid action')

    new_board = [row.copy() for row in board]
    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # checking horizontal winner
    for row in board:
        if len(set(row)) == 1 and row[0] is not EMPTY:
            return row[0]

    # checking vertical winner
    for col in list(zip(*board)):
        if len(set(col)) == 1 and col[0] is not EMPTY:
            return col[0]

    # checking diagonal winner
    if len(set([board[0][0], board[1][1], board[2][2]])) == 1 and (board[1][1] is not EMPTY):
        return board[1][1]
    if len(set([board[0][2], board[1][1], board[2][0]])) == 1 and (board[1][1] is not EMPTY):
        return board[1][1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # check if the game is finished horizontally
    for row in board:
        if len(set(row)) == 1 and row[0] is not EMPTY:
            return True

    # check if the game is finished vertically
        for col in list(zip(*board)):
            if len(set(col)) == 1 and col[0] is not EMPTY:
                return True

    # check if the game is finished diagonally
        if len(set([board[0][0], board[1][1], board[2][2]])) == 1 and (board[1][1] is not EMPTY):
            return True
        if len(set([board[0][2], board[1][1], board[2][0]])) == 1 and (board[1][1] is not EMPTY):
            return True

    # check if the game is finished by draw
        if all(block is not EMPTY for row in board for block in row):
            return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    _winner = winner(board)
    if _winner == X:
        return 1
    elif _winner == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def min_value(board):
        if terminal(board):
            return utility(board)
        min_utility = float('inf')
        best_action = None
        for action in actions(board):
            new_board = result(board, action)
            value = max_value(new_board)
            if type(value) == list:
                value = value[0]
            if value < min_utility:
                min_utility = value
                best_action = action
        return [min_utility, best_action]

    def max_value(board):
        if terminal(board):
            return utility(board)
        max_utility = float('-inf')
        best_action = None
        for action in actions(board):
            new_board = result(board, action)
            value = min_value(new_board)
            if type(value) == list:
                value = value[0]
            if value > max_utility:
                max_utility = value
                best_action = action
        return [max_utility, best_action]

    if player(board) == X:
        return max_value(board)[1]
    return min_value(board)[1]
