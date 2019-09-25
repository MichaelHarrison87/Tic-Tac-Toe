from collections import namedtuple

class Player:
    def __init__(self, name, player_type, token):
        assert player_type.lower() in ('human', 'computer'), 'Player must be a \'Human\' or \'Computer\'.'
        self.player_id = None  # Keeps track of their 
        self.name = name.capitalize()
        self.type = player_type.capitalize()
        self.token = token

    def __str__(self):
        player_named_tuple = namedtuple('Player', ['name', 'type', 'token'])
        return str(player_named_tuple(self.name, self.type, self.token))

    def __hash__(self):
        """Player must be hashable, for use as dict keys."""
        return hash(str(self))
    
    def __eq__(self, other):
        return str(self) == str(other)
        

class ComputerPlayer(Player):
    """Allows for Computer Players with different algorithms ("brains")"""
    def __init__(self, name, token, algorithm):
            super().__init__(name, 'Computer', token)
            self.algorithm = algorithm
    
    def __str__(self):
        computer_named_tuple = namedtuple('ComputerPlayer', ['name', 'token', 'algorithm'])
        return str(computer_named_tuple(self.name, self.token, self.algorithm))
        

class HumanPlayer(Player):
    """This object just makes it clear the player is to be a human player (not a computer)"""
    def __init__(self, name, token):
            super().__init__(name, 'Human', token)
    
    def __str__(self):
        human_named_tuple = namedtuple('HumanPlayer', ['name', 'token'])
        return str(human_named_tuple(self.name, self.token))
