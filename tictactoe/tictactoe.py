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
    raise NotImplementedError


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
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
