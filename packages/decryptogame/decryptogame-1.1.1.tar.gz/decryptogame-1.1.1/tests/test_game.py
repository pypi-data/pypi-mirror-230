import pytest
from decryptogame.game import Game
from decryptogame.components import GameData, Note


@pytest.fixture
def default_game():
    return Game()

class TestGame:
    def test_default_values(self, default_game):
        assert not default_game.notesheet
        assert default_game.data == GameData()
        assert not default_game.game_over()

    def test_kw_only(self):
        with pytest.raises(TypeError):
            Game(lambda x: x)

    def test_private_data(self, default_game):
        game_data = default_game.data
        game_data.rounds_played += 1
        assert game_data.rounds_played != default_game.data.rounds_played

    def test_default_end_conditions(self, default_game):
        round_mid_game_data = GameData(rounds_played=7)
        round_end_game_data = GameData(rounds_played=8)
        assert not default_game.game_over(round_mid_game_data)
        assert default_game.game_over(round_end_game_data)

        miscommunications_mid_game_data = GameData(miscommunications=[1,1], rounds_played=2)
        miscommunications_end_game_data = GameData(miscommunications=[1,2], rounds_played=2)
        assert not default_game.game_over(miscommunications_mid_game_data)
        assert default_game.game_over(miscommunications_end_game_data)

        interceptions_mid_game_data = GameData(interceptions=[1,1], rounds_played=2)
        interceptions_end_game_data = GameData(interceptions=[1,2], rounds_played=2)
        assert not default_game.game_over(interceptions_mid_game_data)
        assert default_game.game_over(interceptions_end_game_data)

    def test_process_round_notes(Self, default_game):
        # one miscommunication among first team, one interception of second team by first
        round_notes = [
            Note(clues=("a", "b", "c"), attempted_interception=(2, 3, 1), attempted_decipher=(2, 3, 1), correct_code=(4, 3, 1)),  # miscommunication
            Note(clues=("dog", "foot", "bar"), attempted_interception=(2, 1, 3), attempted_decipher=(2, 1, 3), correct_code=(2, 1, 3)) # interception
        ]

        # first round should not count interceptions
        default_game.process_round_notes(round_notes)
        assert default_game.data == GameData(miscommunications=[1, 0], rounds_played=1)

        default_game.process_round_notes(round_notes)
        assert default_game.data == GameData(interceptions=[1,0],miscommunications=[2, 0], rounds_played=2)
    
    def test_configurable(self):
        # no miscommunications or interceptions
        first_round_notes = [
            Note(clues=("try", "b", "c"), attempted_interception=(2, 1, 3), attempted_decipher=(1, 2, 3), correct_code=(1, 2, 3)),
            Note(clues=("bat", "dot", "ply"), attempted_interception=(4, 1, 3), attempted_decipher=(3, 1, 4), correct_code=(3, 1, 4))
        ]
        # no miscommunications, one interception of first team by second
        second_round_notes = [
            Note(clues=("apple", "bot", "core"), attempted_interception=(2, 1, 3), attempted_decipher=(2, 1, 3), correct_code=(2, 1, 3)), # interception
            Note(clues=("ant", "bee", "cry"), attempted_interception=(2, 4, 3), attempted_decipher=(4, 1, 3), correct_code=(4, 1, 3))
        ]
        # one miscommunication among first team, one interception of second team by first
        third_round_notes = [
            Note(clues=("abs", "cob", "crap"), attempted_interception=(2, 3, 1), attempted_decipher=(2, 3, 1), correct_code=(4, 3, 1)),  # miscommunication
            Note(clues=("army", "bone", "arc"), attempted_interception=(2, 1, 3), attempted_decipher=(2, 1, 3), correct_code=(2, 1, 3)) # interception
        ]

        notesheet = [first_round_notes, second_round_notes, third_round_notes]

        rounds_played = len(notesheet)

        game = Game(notesheet=notesheet)

        assert game.data == GameData(miscommunications=[1,0], interceptions=[1,1], rounds_played = rounds_played)