"""Simulate Decrypto with custom teams and game settings.

Modules exported by this package:

- `generators`: Provide clue and code generators. These are used to help initialize teams or rounds, but can be replaced with custom input.
- `teams`: Provide team interfaces/protocols and ready-to-go implementations. The CommandLineTeam can be used for fast developer interaction.
- `play`: Provide game and round procedures. They have been brought into the namespace for convenience.
- `game`: Provide a game object which manages game state, and scoring rules. Game has been brought into the namespace for convenience.
- `components`: Provide several game components. They have been brought into the namespace for convenience.
- `end_criteria`: EndConditions which determine when a game ends, and the winner or loser.
"""
from decryptogame.game import Game
from decryptogame.components import GameData, Note, TeamName
from decryptogame.play import play_game, play_round