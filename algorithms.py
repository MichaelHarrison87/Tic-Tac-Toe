import random

def sequential(board):
    """Returns the first available empty cell"""
    if not board.empty_cells:
        return None
    return board.empty_cells[0]


def random_search(board):
    if not board.empty_cells:
        return None
    return random.sample(board.empty_cells, 1)[0] # sample returns a list - so get its first element