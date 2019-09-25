### Ideas  
Create some exceptions? E.g. BadMove - e.g. already played, out-of-bounds
Create a Game class - to manage the players and the board; and game set-up/exit
Factor classes into own modules?
New victory condition: sequences of k characters in a single dircection. Default game is k=3 on 
a 3x3 board, but could alter k for bigger boards: e.g. k=3 on a 5x5 board vs default k=5 
Allow boards of arbitrary dimension
Put onto the web with user front-end?
Record move history - and allow undo/redo?
Add an AI/Computer Opponent - who plays optimally

Aim is to extend to a suite of games, that can use some generic objects e.g. Game, Player, GameSession and we can then use these across all games (e.g. track winrate by player for each game he plays)


Alternative win condition (e.g. for >2 players) could be to score sequences of adjacent tokens
e.g. 2 tokens in a row/col/ = 1 point; 3 tokens = 2 points etc

Can create "obstacles" on the board - cells where you can't play a move - by adding non-player tokens
to it

Implement Go?