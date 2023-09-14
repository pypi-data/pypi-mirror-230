import pytest
from decryptogame.components import GameData, Note


class TestGameData:
    # simple game data is stored seorately so plies are tenable
    def test_default(self):
        game_data = GameData()

        assert game_data.miscommunications[0] == 0
        assert game_data.miscommunications[0] == 0

        assert game_data.interceptions[1] == 0
        assert game_data.interceptions[1] == 0

        assert game_data.rounds_played == 0

    def test_kw_only(self):
        with pytest.raises(TypeError):
            game_data = GameData(0)

    def test_copyable(self):
        data = GameData(interceptions=[1,1], miscommunications=[1,1], rounds_played=2)
        
        # pure copy
        data_copy = data.copy()

        assert data == data_copy

        data_copy.rounds_played += 1

        assert data.rounds_played != data_copy.rounds_played

        data_copy.miscommunications[0] += 1

        assert data.miscommunications != data_copy.miscommunications



class TestNote:

    def test_kw_only(self):
        with pytest.raises(TypeError):
            Note(0)

    def test_configurable(self):
        note = Note(clues=("a", "b", "c"), attempted_decipher=(2, 3, 1), attempted_interception=(1, 3, 2), correct_code=(4, 3, 1))
        
        assert note.clues == ("a", "b", "c")
        assert note.attempted_decipher == (2, 3, 1)
        assert note.attempted_interception == (1, 3, 2)
        assert note.correct_code == (4, 3, 1)
    