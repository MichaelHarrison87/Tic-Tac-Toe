
class BoardIterator:
    """
    Class used by Board's __iter__ method - acts as an iterator over the cells of the 2D board
    As we iterate over the board, it's useful to know what row/col number we're at
    e.g. (0,0) for top-left corner, (1,2) for 2nd row, 3rd column etc (recall, 0-indexed)
    
    We track this using self.row_id and self.col_id - however these keep track of the
    /previous/ row/col values since calls to __next__ increment them AFTER returning the cell value.
    So, for instance, the first call to __next__ would return the value at (0,0) but then increment
    the index to (0,1) - so that board_iter.col_id would equal 1 instead of 0 
        
    But we don't label them as, e.g., prev_row_id as the access pattern board_iter.row_id
    makes more sense. As we'd want the cell value at (0,0) to be associated with row_id 0 and
    col_id 0.
    
    Instead the row/col to return with the next call to __next__ are stored as self.next_row_id,
    self.next_col_id - and these are then incremented after getting the cell value.
    """
    def __init__(self, array):
        self.board = array
        self.num_rows = len(self.board)
        
        self.next_row_id = 0
        self.next_col_id = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.row_id = self.next_row_id
        self.col_id = self.next_col_id
        
        try:
            cell =  self.board[self.next_row_id][self.next_col_id]
        except IndexError:
            raise StopIteration()
        else:
            if self.next_col_id < (len(self.board[0]) - 1):     # iterating over a row
                self.next_col_id += 1
            else:   # in last column, move to start of next row
                self.next_col_id = 0
                self.next_row_id += 1
        # At the end of the final row, incrementing the row will result in the IndexError above
        # on the next next() call, and hence StopIteration() 
        return cell
    
    @property
    def row(self):
        return self.board[self.row_id]
    
    @property
    def col(self):
        return [self.board[row][self.col_id] for row in range(self.num_rows)]
    
                

class Board:
    
    def __init__(self, num_rows = 3, num_cols = 3):
        
        # Board must be square:
        assert num_rows == num_cols, 'Boards must be square (i.e. num rows = num columns)'
        
        # Store the board as 2D array (nested lists), of player "tokens" (or some token for empty cells)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_cells = num_rows * num_cols
        
        # Instantiate the board
        self.empty = ' '    # token for empty cells
        self.board = [[self.empty for i in range(num_cols)] 
                            for j in range(num_rows)]
        
        # Lists to hold the history of moves played on the board (and associated tokens)
        self.played_positions = []
        self.played_tokens = []
    
        # Store row, col numbers of remaining free cells
        self.empty_cells = [(i, j) for i in range(num_cols) for j in range(num_rows)]
    
    
    # Properties below allow for access of specific parts of the board
    @property
    def rows(self):
        return self.board
    
    @property
    def columns(self):
        return [[self.board[row][col] for row in range(self.num_rows)] for col in range(self.num_cols)]
    
    @property
    def main_diagonal(self):
        return [self.board[i][i] for i in range(self.num_rows)]
    
    @property
    def anti_diagonal(self):
        return [self.board[i][self.num_cols - i -1] for i in range(self.num_rows)]
    
    
    def __getitem__(self, index):
        """Make board slicable  - i.e. access elements via Board[row][col].
        Sine this returns a list, that can then itself be sliced, i.e. [row][col]"""
        return self.board[index]
    
    
    def __str__(self):
        pretty = ''
        for row in self.board:
            pretty += str(row) + '\n'
        return pretty
    
    def play(self, row, col, token):
        # Check input
        if (row, col) in self.played_positions:
            raise IndexError(f'Invalid Positon - ({row + 1},{col + 1}) has already been played!')
        
        # If good, play the move
        self.board[row][col] = token
        
        # Update history
        self.played_positions.append((row, col))
        self.played_tokens.append(token)
        self.empty_cells.remove((row, col))
                
    
    def winner(self):
        """Returns the winning token, if there is one.
        A potential optimisation here could be to only check the row/col/diagonal of 
        the most-recent value put onto the board - rather than check all rows/columns as we do below"""        
        # Check rows
        for row in self.rows:
            if all(row[0] == cell for cell in row):     # all() applies over the columns in the row
                winner = row[0]
                if winner is not self.empty:
                    return winner
             
        # Check columns
        for column in self.columns:
            if all(column[0] == cell for cell in column):     # all() applies over the rows in the column
                winner = column[0]
                if winner is not self.empty:
                    return winner
            
        # Check the main diagonal - top left to bottom right
        if all(self.main_diagonal[0] == cell for cell in self.main_diagonal):
                winner = self.main_diagonal[0]
                if winner is not self.empty:
                    return winner
        
        # Check the anti-diagonal - top right to bottom left
        if all(self.anti_diagonal[0] == cell for cell in self.anti_diagonal):
                winner = self.anti_diagonal[0]
                if winner is not self.empty:
                    return winner
        
        # No winners - return None:
        return None

    def full(self):
        """Checks if the board is full of tokens (and so have to end the game)"""
        return not self.empty_cells

    def __iter__(self):
        return BoardIterator(self.board)
    
    def copy(self):
        new_board = type(self)(self.num_rows, self.num_cols)
        new_board.board = [row.copy() for row in self.rows]
        new_board.played_positions = self.played_positions.copy()
        new_board.played_tokens = self.played_tokens.copy()
        new_board.empty_cells = self.empty_cells.copy()
        return new_board
    
    def __eq__(self, other):
        return (self.board == other.board)

    def recitfy_game_history(self):
        """Utility function to correct the lists of played positions/tokens and empty cells.
        Mainly used by the rotate() and reflect() methods after rotating/reflecting their new
        board's board attribute.
        
        Note: this doesn't capture the order of moves, just that the lists will contain all the correct
        items (but they may be in wrong order).
        """
        # Overwrite the lists of played positions/tokens and empty cells to reflect the new board
        board_iter = iter(self)
        self.empty_cells = []
        self.played_positions = []
        self.played_tokens = []
        
        for cell in board_iter:
            position = (board_iter.row_id, board_iter.col_id)
            if cell is self.empty:
                self.empty_cells.append(position)
            else:
                self.played_tokens.append(cell)
                self.played_positions.append(position)
        
    
    def rotate(self, degrees):
        assert degrees in (90, 180, 270), 'degrees must be 90, 180 or 270'
        
        new_board = Board(self.num_rows, self.num_cols)
        if degrees == 90:
            new_board.board = [column[::-1] for column in self.columns]  # Swap columns for rows, but invert each column first (top-left cell moves to top-right - i.e. top of first column becomes end of first row)
        elif degrees == 180: 
            new_board.board = [row[::-1] for row in self.rows[::-1]]  # Invert each row, and invert the order of rows (top-left cell moves to bottom-right)
        elif degrees == 270:
            new_board.board = [column for column in self.columns[::-1]] # Swap columns for rows, in reverse column order (last column moves to first row)
        else:
            return None
        
        new_board.recitfy_game_history()                
        return new_board

    def reflect(self, axis):
        axis = axis.lower()
        assert axis in ('horizontal', 'h', 'vertical', 'v', 'main diagonal', 'md', 'anti-diagonal', 'ad')
        
        new_board = self.copy()
        
        if axis in ['horizontal', 'h']:
            new_board.board = [row for row in self.rows[::-1]]  # Rows in reverse order
        elif axis in ['vertical', 'v']:
            new_board.board = [row[::-1] for row in self.rows]  # Invert each row 
        elif axis in ['main diagonal', 'md']:
            new_board.board = [column[::-1] for column in self.columns[::-1]]  # Swap columns for rows, in reverse row order, inverting each row first (e.g. 3rd cell in first row becomes 3rd to last cell in last column) 
        elif axis in ['anti-diagonal', 'ad']:
            new_board.board = [column for column in self.columns] # Swap columns for rows
        else:
            return None
        
        new_board.recitfy_game_history()
        return new_board
        

    # Note: below must be a property, as otherwise creating isomorphisms in __init__ results in 
    # infinite recursion since the rotate() and reflect() methods also create new boards
    @property
    def isomorphisms(self):
        """Returns set of boards isomorphic to self, namely:
        90, 180, 270 degree rotations, reflections in all axes (horizontal, vertical, both diagonals)
        Also include self in the list of isomorphims, so that all boards are isomorphic to themselves"""
        rotations = [self.rotate(degrees) for degrees in (90, 180, 270)]
        reflections = [self.reflect(axis) for axis in ('h', 'v', 'md', 'ad')]
        
        # Some rotations/reflections give the same result, depending on the board's state 
        # - so remove duplicates 
        # (could have used a set here but required boards to be hashable - which I don't want
        # them to be, as they're mutable).
        rotations = [self] + [board for board in rotations if board != self]
        reflections = [board for board in reflections if board not in rotations]
        return rotations + reflections  

    def isomorphic_to(self, other):
        return self in other.isomorphisms

if __name__ == '__main__':
    b = Board(7,7)
    b.play(0, 0, 'O')
    print('Original board:')
    print(b)
    
    b2 = Board(7,7)
    b2.play(0, 6, 'O')
    print('Board 2:')
    print(b2)
    print(b.isomorphic_to(b2), b2.isomorphic_to(b))
    
    
    b3 = Board(7,7)
    b3.play(0, 6, 'X')
    print('Board 3:')
    print(b3)
    print(b.isomorphic_to(b3), b3.isomorphic_to(b))
    
    # b.play(1, 1, 'X')
    # b.play(0, 2, 'O')
    # b.play(2, 2, 'X')
    # b.play(2, 0, 'O')

    



    for i, iso in enumerate(b.isomorphisms):
        print(f'\nIsomorphism {i+1}')
        print(iso)
        print('empty cells:', iso.empty_cells)
        print('played positions:', iso.played_positions)
        print('played tokens:', iso.played_tokens)