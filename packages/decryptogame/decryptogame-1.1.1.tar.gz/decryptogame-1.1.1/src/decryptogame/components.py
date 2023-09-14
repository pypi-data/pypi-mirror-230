import dataclasses
from copy import deepcopy
from collections.abc import Sequence
from enum import IntEnum

Keywords = Sequence[str]
Code = tuple[int]
Clue = tuple[str]

class TeamName(IntEnum):
    """Enumeration representing the team names.

    Attributes:
        WHITE (int): Team name for the White team, with a value of 0.
        BLACK (int): Team name for the Black team, with a value of 1.
    """
    WHITE = 0
    BLACK = 1

    def __repr__(self):
        """Custom representation for TeamName enumeration values.

        Returns:
            str: A formatted string representation of the TeamName.
        """
        return f"<{self.name}: {self.value}>"
    
    def __str__(self):
        """Custom string method for TeamName enumeration values.

        Returns:
            str: The name of the team.
        """
        return str(self.name)

@dataclasses.dataclass(kw_only=True)
class GameData:
    """Class representing the game data. It's main use would be for strategizing or simulating plies.

    Attributes:
        rounds_played (int, optional): The number of rounds played. Defaults to 0.
        miscommunications (Sequence[int], optional): The miscommunication counts for each team. Defaults to [0, 0].
        interceptions (Sequence[int], optional): The interception counts for each team. Defaults to [0, 0].
    """
    rounds_played: int = 0
    miscommunications: Sequence[int] = dataclasses.field(default_factory=lambda: [0, 0])
    interceptions: Sequence[int] = dataclasses.field(default_factory=lambda: [0, 0])

    def copy(self):
        """Create a deep copy of the GameData object.

        Returns:
            GameData: A deep copy of the GameData object.
        """
        return deepcopy(self)

@dataclasses.dataclass(kw_only=True)
class Note:
    """Class representing a note with information about the code, clues, attempted decipher and interception of a team in a given round.

    Attributes:
        clues (Clue): The clue information associated with the note.
        attempted_interception (Code): The code for the attempted interception.
        attempted_decipher (Code): The code for the attempted decipher.
        correct_code (Code): The correct deciphered code.
    """
    clues: Clue
    attempted_interception: Code
    attempted_decipher: Code
    correct_code: Code
