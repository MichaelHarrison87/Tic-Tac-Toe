from functools import partial

from board import Board
from game import Game
from player import HumanPlayer, ComputerPlayer
from algorithms import sequential, random_search
from full_tree_search import full_tree_search

# Intialise board
board = Board()


# Create players - have to use partial application to get a version of tree_search for each token
player_set = {'O': 'Alice', 'X': 'Bob'} # , 'Y': 'Charles', 'Z': 'Dennis'}
tree_search = full_tree_search(board, list(player_set.keys())) 

players = [ComputerPlayer(value, key, partial(tree_search, token = key)) 
           for key, value in player_set.items()]


# Create and play the game
g = Game(board, players)
g.play_game()