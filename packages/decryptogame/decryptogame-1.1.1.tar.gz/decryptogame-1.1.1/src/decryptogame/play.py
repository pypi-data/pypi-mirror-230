from collections.abc import Iterable, Sequence
from decryptogame.components import Code, Note
from decryptogame.game import Game
from decryptogame.generators import RandomCodes
from decryptogame.teams import Team, TeamContext
from functools import partial
from typing import Optional
    
def play_game(teams: Sequence[Team], *, 
              game: Game = None, 
              round_codes: Iterable[Sequence[Code]] = None, 
              round_limit: Optional[int]=None
              ) -> Game:
    """Play a game of Decrypto. This function will change the game object as the rounds are played.

    Args:
        teams (Sequence[Team]): The pair of teams participating in the game.
        game (Game): The Decrypto game object. If None, a standard game will be generated.
        round_codes (Iterable[Sequence[Code]], optional): Iterable of codes for each round. If None, random codes will be generated.
        round_limit (Optional[int], optional): The maximum number of rounds to play. If None, the game continues until completion.
    
    Returns:
            Game: The game state after play.
    """
    game = game if game is not None else Game()
    round_codes = round_codes if round_codes is not None else RandomCodes([team.keywords for team in teams])
    for rounds_played, codes in enumerate(round_codes):
        if game.game_over() or rounds_played == round_limit:
            break
        play_round(teams, game, codes)
    return game


def play_round(teams:Sequence[Team], game: Game, codes: Sequence[Code]):
    """Play a single round of Decrypto. The game object will be updated with the round results.

    Args:
        teams (Sequence[Team]): The pair of teams participating in the game.
        game (Game): The Decrypto game object which encodes the current state.
        codes (Sequence[Code]): The codes for the current round.
    """
    # each member may need information about its team and the game to make proper decisions
    context = [TeamContext(
                team_name=team_name, 
                keywords=team.keywords, 
                num_opponent_keywords=len(teams[not team_name].keywords),
                game=game
                )
                for team_name, team in enumerate(teams)]

    # each team's encryptor decides the clues
    clues = {}
    for team_name, code in enumerate(codes): 
        team = teams[team_name]
        # give the encryptor the context of its team and the current game state
        clues[team_name] = team.encryptor.decide_clues(code, context[team_name])

    # each team attempts to intercept the opposing team's code
    attempted_interception = {}
    for team_name, code in enumerate(codes):
        team = teams[team_name]
        # give the intercepter the context of its team and the current game state
        opponent = not team_name
        attempted_interception[team_name] = team.intercepter.intercept_clues(clues[opponent], context[team_name])

    # each team attempts to decipher the clues to their code
    attempted_decipher = {}
    for team_name, code in enumerate(codes):
        team = teams[team_name]
        # give the guesser the context of its team and the current game state
        attempted_decipher[team_name] = team.guesser.decipher_clues(clues[team_name], context[team_name])

    # each team reveals their codes and the notes are processed and added to the notesheet
    notes = [Note(clues=clues[team_name],
                  attempted_interception=attempted_interception[team_name],
                  attempted_decipher=attempted_decipher[team_name],
                  correct_code=code
                  ) 
                  for team_name, code in enumerate(codes)]
    game.process_round_notes(notes)
