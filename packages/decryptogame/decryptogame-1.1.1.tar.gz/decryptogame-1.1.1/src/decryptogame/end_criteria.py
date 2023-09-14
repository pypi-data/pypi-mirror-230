from collections import Counter
from decryptogame.game import GameData
from decryptogame.components import TeamName
from typing import Optional, Protocol

MAX_OFFICIAL_MISCOMMUNICATIONS = 2
MAX_OFFICIAL_INTERCEPTIONS = 2
MAX_OFFICIAL_ROUNDS = 8

class EndCondition(Protocol):
    """Interface representing a condition under which a game may end."""

    def game_over(game_data: GameData) -> bool:
        """Check if the game is over based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        ...
    
    def winner(game_data: GameData) -> Optional[TeamName]:
        """Determine the winner of the game based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: The team name of the winner or None if there is no winner (tie or the game is not over).
        """
        ...

    def loser(game_data: GameData) -> Optional[TeamName]:
        """Determine the loser of the game based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: The team name of the loser or None if there is no loser (no game over or multiple players lose).
        """
        ...


class MiscommunicationEndCondition(EndCondition):
    """End condition representing that a game ends if a team has k miscommunication tokens, in which case it loses."""
    
    def __init__(self, k: int = MAX_OFFICIAL_MISCOMMUNICATIONS):
        """Initialize the MiscommunicationEndCondition.

        Args:
            k (int, optional): The number of miscommunication tokens required for the game to end. Defaults to MAX_OFFICIAL_MISCOMMUNICATIONS.
        """
        self.k = k

    def game_over(self, game_data: GameData) -> bool:
        """Check if the game is over due to reaching k miscommunications based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return any(miscommunications == self.k for miscommunications in game_data.miscommunications)
    
    def winner(self, game_data: GameData) -> Optional[TeamName]:
        """Determine the winner of the game based on the provided game data. Since miscommunications determine a loser, None is returned.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: Always returns None for this condition as there is no win condition.
        """
        return None
    
    def loser(self, game_data: GameData) -> Optional[TeamName]:
        """Determine the loser of the game due to reaching k miscommunications based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: The team name of the loser according to this condition, or None if there is no loser yet.
        """
        # if the game has not finished or multiple players lose, the loser is undecided 
        if not self.game_over(game_data) or Counter(game_data.miscommunications)[self.k] > 1:
            return None
        loser = game_data.miscommunications.index(self.k)
        return TeamName(loser)
        

class InterceptionEndCondition(EndCondition):
    """End condition representing that a game ends if a team has k interception tokens, in which case it wins."""

    def __init__(self, k: int = MAX_OFFICIAL_INTERCEPTIONS):
        """Initialize the InterceptionEndCondition.

        Args:
            k (int, optional): The number of interception tokens required for the game to end. Defaults to MAX_OFFICIAL_INTERCEPTIONS.
        """
        self.k = k

    def game_over(self, game_data: GameData) -> bool:
        """Check if the game is over due to reaching k interceptions based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return any(interceptions == self.k for interceptions in game_data.interceptions)
    
    def winner(self, game_data: GameData) -> Optional[TeamName]:
        """Determine the winner of the game due to reaching k interceptions based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: The team name of the winner according to this condition, or None if there is no winner yet.
        """
        # if the game has not finished or multiple players win, the winner is undecided 
        if not self.game_over(game_data) or Counter(game_data.interceptions)[self.k] > 1:
            return None
        winner = game_data.interceptions.index(self.k)
        return TeamName(winner)
    
    def loser(self, game_data: GameData) -> Optional[TeamName]:
        """Determine the loser of the game based on the provided game data. Since interceptions determine a winner, None is returned.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: Always returns None for this condition as there is no loser.
        """
        return None


class RoundEndCondition(EndCondition):
    """End condition representing that a game ends if it reaches k rounds, in which case no winner or loser is decided."""

    def __init__(self, k: int = MAX_OFFICIAL_ROUNDS):
        """Initialize the RoundEndCondition.

        Args:
            k (int, optional): The number of rounds required for the game to end. Defaults to MAX_OFFICIAL_ROUNDS.
        """
        self.k = k

    def game_over(self, game_data: GameData) -> bool:
        """Check if the game is over due to reaching k rounds played based on the provided game data.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        return game_data.rounds_played == self.k
    
    def winner(self, game_data: GameData) -> Optional[TeamName]:
        """Determine the winner of the game based on the provided game data. Since rounds played determines no winner, None is returned.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: Always returns None for this condition as there is no winner.
        """
        return None
    
    def loser(self, game_data: GameData) -> Optional[TeamName]:
        """Determine the loser of the game based on the provided game data. Since rounds played determines no loser, None is returned.

        Args:
            game_data (GameData): The game data to check.

        Returns:
            Optional[TeamName]: Always returns None for this condition as there is no loser.
        """
        return None
    
OfficialEndConditions = lambda: [RoundEndCondition(), MiscommunicationEndCondition(), InterceptionEndCondition()]