
from board import Board
from player import ComputerPlayer
import time

class Game:
    def __init__(self, board, players=None):
        assert isinstance(board, Board), 'Board must be an instance of the Board class'
        self.board = board
        
        if players is None:
            self.players = []
            self.token_lookup = {}
            self.player_counter = {}
        else:
            assert len({player.token for player in players}) == len(players), 'Each player must have a unique token!'
            assert self.board.empty not in [player.token for player in players], f'\'{self.board.empty}\' is not a valid token!'
            
            self.players = players
            self.token_lookup = {player.token: player for player in players}  # maps token to player
            self.player_counter = {players[i]: i+1 for i in range(len(players))} # maps players to player numbers
    
        self.round_num = 1
        self.exit_flag = False   # if True, game should exit (potentially early)
        

    @property
    def winner(self):
        """Gets winning Player, from the board's winning token"""
        if self.board.winner() is None:
            return None
        return self.token_lookup[self.board.winner()] 
    
    def add_player(self, player):
        if player.token in self.token_lookup:
            raise AttributeError(f'Player with token \'{player.token}\' already playing! Pick another token.')
        if (player.token.strip() == '') or (player.token is self.board.empty):
            raise AttributeError(f'Token \'{player.token}\' is not a valid token! Pick another token.')
        
        self.players.append(player)
        self.token_lookup[player.token] = player
        player_id = max(self.player_counter.values()) + 1
        self.player_counter[player] = player_id
        print(f'{player.name} added to the game (Player {player_id}) - playing as {player.token}')
        
    
    def welcome(self):
        print('\nWelcome to Tic-Tac-Toe!')
        print('The players are:')
        for player in self.players:
            print(f'\tPlayer {self.player_counter[player]}: {player.name} ({player.type}) - playing as {player.token}')
    
    
    def play_turn(self, player):
        """A 'turn' is one player's go during a particular round."""
        input('Play turn...')
        print(f'{player.name} to play...\n')
        
        if isinstance(player, ComputerPlayer):
            print('Thinking...')
            time.sleep(1)
            row, col = player.algorithm(self.board)
            self.board.play(row, col, player.token)  # algorithms index from (0,0) - so adjust this to (1,1) etc 
        else:
            print(self.board)
            while True:
                usr_input = input(f'{player.name}, enter a move: ')
                
                if usr_input.lower() == 'exit':
                    print(f'{player.name} exited!')
                    self.exit_flag = True
                    return

                if usr_input.lower() == 'skip':
                    print(f'{player.name} has skipped their go!')
                    return

                row, col = [int(i) for i in usr_input.split(' ')]
                try:
                    self.board.play(row - 1, col - 1, player.token)  # index top-left corner as (1,1) in player input, vs (0,0) everywhere else
                except IndexError as e:
                    print(str(e), 'Play a different position.')
                else:
                    break
        print(f'{player.name} played: ({row + 1}, {col + 1})\n')
        print(self.board)
     
    
    def play_round(self):
        """
        A 'round' is the set of turns for each player.
        E.g. the first round for 3 players is all 3 players taking their first turn.
        """
        print('='*10) # Round separation display
        print(f'Round {self.round_num}:')
        for player in self.players:

            # Player separation display:
            if player != self.players[0]:
                print('-' * 5)

            self.play_turn(player)
            
            # Return if exit conditions are met
            if (self.exit_flag) or (self.winner is not None) or (self.board.full()):
                return
        self.round_num += 1
                 
    
    def play_game(self):
        """A 'game' plays out each round, until a player plays a winning move, or exits, or the board becomes full"""
        self.welcome()
        while (self.winner is None) and (not self.exit_flag) and (not self.board.full()):
            self.play_round()
        self.exit_game()
     
        
    def exit_game(self):
        print('='*10) # Round separation display
        if self.winner is None:
            if self.board.full():
                print('The board is full!')
            print('The game ends in a draw.')
        else:
            print(f'{self.winner.name} has won! Congratulations!')
        print('Exiting game. Thanks for playing...')
        
