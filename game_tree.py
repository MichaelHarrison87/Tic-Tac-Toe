from collections import namedtuple, Counter
from itertools import permutations
from time import time
from tqdm import tqdm

from board import Board
from player import ComputerPlayer
from algorithms import sequential

# Full game tree has 986,409 nodes; but we can trim this massively by noting certain boards are isomorphic
# to each other - e.g. all first moves in a corner are equivalent.
# Isomorphisms:
# Rotation: by 90, 180, 270 degrees about the center of the board (note 90 degree clockwise = 270 degree anti-clockwise)
# Reflections: along horizontal or vertical axes, and along main- and anti-diagonal axes
# Or combinations of these (although combinations should be equivalent to one of the operations in isolation)
# Could reflect these isomorphisms when comparing board equality

class Node:
    """
    Each node represents a turn of the game - we create it with a board and the move to play.
    Then we play the move (during __init__) and update the game state (has anyone won, or is it a draw)
    
    Note: the list of tokens is assumed to be in the order of play - with the first element being
    the token played during the turn that the node represents. So then as child nodes are created,
    we "rotate" the list of tokens - so that the next token to play is first in the list for the children.
    E.g. rotating ['O', 'X', 'Y'] gives ['X', 'Y', 'O']; rotating this gives ['Y', 'O', 'X'] etc...
    
    A slight awkwardness is that at the root we effectively initialise at "turn 0" - with no move to play. 
    So that the children of the root represent the first moves in the game. Thus if we rotated the list
    of tokens when creating these children, the token sequence would be out-of-order. Or else, we'd have
    to initialise with a token list that represented the desired play order /after/ being rotated - very
    annoying!
    
    So instead, at the root (i.e. parent is None) we don't rotate the tokens list - so that we can initialise
    the tree with the tokens in the desired play order.
    
    However this /doesn't/ hold if the root is initialised with a move - in which case, it should play the move    
    
    
    NOTE: after eliminating isomorphic positions, my run of the game tree has 8306 nodes, with turn breakdown:
    Counter({7: 2735, 6: 2512, 5: 1259, 8: 1176, 4: 342, 9: 201, 3: 66, 2: 12, 1: 3, 0: 1})
    """
    
    def __init__(self, board, tokens, move = None, parent = None):
        self.board = board.copy()
        self.tokens = tokens
        self.move = move
        self.parent = parent
        
        # Get the token to be played this turn (excpet at the root - which is "turn 0"), and play it
        if (self.parent is None) and (self.move is None):
            self.token_played = None
        else:
            self.token_played = self.tokens[0]
        
        if self.move is not None:
            self.board.play(move[0], move[1], self.token_played)
        
        # Update game state after the move
        self.winner = self.board.winner()
        self.board_full = self.board.full()
        
        # If board is full, but no winner - it's a draw:
        if (self.winner is None) and self.board_full:
            self.winner = 'Draw'
        
        # If there's no winner/not a draw, get set of possible next moves (else return None) 
        if self.winner is None:
            self.next_moves = [move for move in self.board.empty_cells]
        else:
            self.next_moves = None
    
    @property
    def turn_number(self):
        if (self.parent is None):
            if (self.move is None):
                return 0
            else:
                return 1    # if root initialised with a move, that's the first move
        else:
            return self.parent.turn_number + 1
    
     # Note: if we try to initialise the list of children in Node's __init__ method, we end up recursively
     # creating the whole tree, since we create new Node's when creating the list of children.
     # Instead leave this as an @property, so the children are only created when called (and hence, 
     # we don't end up creating all grandchildren, great-grandchildren etc). Although this is cumbersome
     # if we want to repeatedly access a node's children
    @property 
    def children(self):
        
        # If turn produces winner, stop the tree there - don't want to make further moves
        if self.winner is not None:
            return None
        
        # Don't rotate tokens list at the root with no move - as want next nodes to represent first turn, with first token in the tokens list
        if (self.parent is None) and (self.move is None):     
            tokens_rotate = self.tokens
        else:
            tokens_rotate = self.tokens[1:] + self.tokens[:1]
        
        # Out of possible next moves, we want the ones that are unique up to isomorphism    
        child_nodes = []
        for move in self.next_moves:
            child = Node(self.board, tokens_rotate, move, parent = self)
            if not child_nodes:
                child_nodes.append(child)
            elif all(not child.isomorphic_to(other) for other in child_nodes):  # only add to child node list if candidate child is not isomorphic to any of them
                child_nodes.append(child) 
        return child_nodes

    @property
    def siblings(self):
        if self.parent is None:
            return None
        siblings = self.parent.children
        return [sibling for sibling in siblings if sibling != self]
    
    
    def __repr__(self):
        node_nt = namedtuple('Node', ['move', 'token'])
        return repr(node_nt(self.move, self.token_played))
    
    def __iter__(self):
        return NodeIterator(self)
    
    def __eq__(self, other):
        """Two nodes are the same if they are at the same position in the tree"""
        return (self.move == other.move) and \
               (self.token_played == other.token_played) and \
               (self.board == other.board)
            #    (self.turn_number == other.turn_number) and \
            #    all(i == j for i, j in zip(self.board.played_positions, other.board.played_positions))

    def isomorphic_to(self, other):
        """Utility to check if two nodes produce isomorphic boards"""
        return self.board.isomorphic_to(other.board)


class NodeIterator:
    
    def __init__(self, node):
        self.node = node
        self.visited_nodes = []
        
    def __iter__(self):
        return self
    
    
    # Write depth_first and breadth-first versions of this function
    def depth_first_search(self, current_node):
        """
        Search priority for depth-first search is:
            1. Move to current node's first unvisited child
            2. If there are none, move to parent node's first unvisited child
        This applies recursively, so that we iterate back through node's ancestors if parent has no unvisited children
        
        RECURSION PROBABLY POOR TECHNIQUE HERE - INSTEAD TRACK ANCESTOR LEVELS
        """
        def get_unvisited_items(items):
            if (not items) or (items is None):
                return None
            unvisited_items = [item for item in items if item not in self.visited_nodes]
            if not unvisited_items:     # i.e. unvisited items is empty, as all items have been visited
                return None
            return unvisited_items
        
        # Get list of unvisited children - set to None if current_node has no children, or no unvisited ones
        unvisited_children = get_unvisited_items(current_node.children)
            
        # If at root, with no unvisited children (and have also visited root itself), stop iterating
        if (unvisited_children is None) and (current_node in self.visited_nodes):
            
            if current_node.parent is None:
                raise StopIteration()
            
            # But if not at root, progress up the tree until get a node with children  
            while get_unvisited_items(current_node.children) is None:
                if current_node.parent is None:
                    break 
                current_node = current_node.parent
                
            
        # Now, at a node with unvisited children, we look for the next node
        if unvisited_children is not None:
            next_node = unvisited_children[0]
        else:
            next_node = current_node     # No unexplored nodes left, so don't update self.node - the next call to next() will get caught in the StopIteration logic above
        
        
        # Update self.node to be next_node - so that subsequent calls to next() use this 
        self.node = next_node
        
        # If not current node not visited, add current node to list of visited nodes, then return current node
        if current_node not in self.visited_nodes:
            self.visited_nodes.append(current_node)
            return current_node
        else:
            return self.depth_first_search(next_node)
    
    def __next__(self):
        return self.depth_first_search(self.node)
        
        

if __name__ == '__main__':
    t0 = time()
    board = Board()      # WARNING FULL 3x3 GAME TREE HAS ~1 million nodes
    # board.play(1,1,'O')
    # board.play(2,0,'X')
    # board.play(2,1,'O')
    # board.play(1,2,'X')
    # board.play(2,2,'O')
    # board.play(0,1,'X')
    
    node = Node(board, ['O', 'X'])
    elapsed = time() - t0
    print(f'Node Initialised: {elapsed/60:.0f} mins {elapsed % 60:.0f} secs')
    # print(node.board)
    # print(node.children)
    
    turn_counter = Counter()
    node_iter = iter(node)
    for n in tqdm(node_iter):
        # print(i)
        # input('HOLD')
        # print(f'{i}: {n} winner: {n.winner} [turn {n.turn_number}]')
        turn_counter[n.turn_number] += 1
        # print(n.board)
        # print('CHILDREN:', n.children)
        # print('VISITED NODES:', node_iter.visited_nodes)
        # print('----')
    print(turn_counter)
    elapsed = time() - t0
    print(f'ELAPSED: {elapsed/60:.0f} mins {elapsed % 60:.0f} secs')
