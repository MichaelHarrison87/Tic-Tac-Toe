"""
Examine all permutations of moves to determine optimal moves
Note there num_cells! permuatations of moves, e.g. 9! for 3x3 board
Even for a 5x5 board - this becomes unfeasible: 25! ~= 10**25!

Use a closure here - upon initialisation, it creates the tree based on the board, and
list of players. Then subsequent calls (to lookup moves) don't need to re-create this
tree each time. (It's not actually a tree, just a dict of move sequence permuations to eventual outcome
 - i.e. draw or winning token)

NOTE: the inner function takes the token as an argument, but we don't allow this arg when
calling it for a specific player (can only pass board - as for the other functions). So we 
can use partial application to create token-specific versions of the inner function 

Alternatively, could use a class with a __call__ method - to make it callable (and hence usable
when supplied in lieu of a function).


Ideally want to use a tree-based approach here - perhaps a defauldict with a defaultdict as its
default callable (cf: list) is a useful data structure for this? (in lieu of dict of dicts of dicts...) 

NOTE: Searching over permutations effectively searches over all possible orderings of moves;
can instead search over the (much smaller!) state space, ignoring order - for 3x3 board with 2 
players this i 3^9 = 19_683 - cf 9! ~= 360_000 - all possible combos of blank, O, X across the 9 cells
So 5x5 with 3 players this is: 4^25 ~= 10^15 - cf 25! ~= 10^25.
"""
import random
import statistics

from collections import defaultdict
from itertools import permutations
from tqdm import tqdm
from board import Board


def full_tree_search(board, tokens):

    print('Initialising search tree...')

    # Minimax score values
    WIN = 100
    LOSS = -100
    DRAW = 0
    
    # Setup - all code up to inner function (get_move) definition runs upon intialisation
    num_players = len(tokens)

    moveset = board.empty_cells
    move_permuations = list(permutations(moveset))

    # USE THREADING/MULTIPROCESSING HERE - probably multiprocessing as this is a CPU-bound task?
    winners = {}   # dict matching each permuation to its eventual winner (or draw)
    for perm in tqdm(move_permuations):
        board_copy = board.copy()
        
        player_id = 0
        for move in perm:
            # Play the moves, get the ultimate winner
            board_copy.play(move[0], move[1], tokens[player_id])
            if board_copy.winner() is not None:
                winners[perm] = board_copy.winner()
                break
            player_id = (player_id + 1) % num_players
        else:
            winners[perm] = 'Draw'   

    # Closure - subsequent calls call this
    def get_move(board, token):
        
        # Edge case - only 0 or 1 potential moves 
        if not board.empty_cells:
            return None
        elif len(board.empty_cells) == 1:
            return board.empty_cells[0]
        
        # Get subset of the full move tree containing the moves played so far
        if not board.played_positions:      # played_positions empty, i.e. we're on the first move
            num_moves = 0
            winners_subset = winners
        else:
            num_moves = len(board.played_positions)
            perm_subset = [perm for perm in move_permuations 
                           if perm[:num_moves] == tuple(board.played_positions)]
            
            winners_subset = {perm: winners[perm] for perm in perm_subset}
        
        # Create mapping of potential next moves, with a list of the eventual winners 
        print('winners subset:', set(winners_subset.values()))
        next_moves = defaultdict(list)
        for perm, winner in winners_subset.items():
            if winner == token:
                value = WIN
            elif winner == 'Draw':
                value = DRAW
            else:
                value = LOSS
            next_moves[perm[num_moves]].append(value)
        
        
        ## SOME ISSUES HERE - WANT MINIMAX CONDIITON (CURRENTLY CAN LET OPPONENT WIN, 
        # presumably since the blocking move results in fewer winning permuations)
        # Need some notion of what the oppoent will play
        # Another issue is: doesn't search for the /quickest/ route to victory
        #
        # E.g. with only 1 player - on first move, all cells have same velue as all lead to win
        # But on next move, all cells still have same value as all still lead to a win
        # (so might pick a cell at random that doesn't build up the row/col/diagonal of 3)
        
        # Get aggregate scores
        agg_scores = {move: statistics.mean(value) for move, value in next_moves.items()}
        print('agg_scores:', agg_scores)
        
        # And hence list of best moves - i.e. highest agg score; then return one of these at random
        best_moves = [move for move, value in agg_scores.items() if value == max(agg_scores.values())]
        return random.sample(best_moves, 1)[0]

    return get_move


