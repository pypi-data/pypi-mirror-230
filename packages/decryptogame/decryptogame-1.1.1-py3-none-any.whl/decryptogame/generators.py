import random
from collections.abc import Sequence
from decryptogame.components import Keywords, Code
import decryptogame.official_words.english as english
from itertools import permutations
from typing import Optional


DEFAULT_CODE_LENGTH = 3
DEFAULT_CARD_LENGTH = 4

class RandomCodes:
    """Generator for generating random codes for each team in the Decrypto game.

    Args:
        keyword_cards (Sequence[Keywords]): The keyword cards for each team.
        code_lengths (Sequence[int], optional): The lengths of the codes for each team. Defaults to DEFAULT_CODE_LENGTH.
        seed (int, optional): The random seed for consistent code generation. Defaults to None.

    Yields:
        tuple[Code, Code]: A tuple containing the randomly generated codes for each team.
    """
    def __init__(self, keyword_cards: Sequence[Keywords], code_lengths: Sequence[int] = None, seed: Optional[int] = None):
        self.code_lengths = code_lengths if code_lengths is not None else [DEFAULT_CODE_LENGTH] * len(keyword_cards)
        self.random = random.Random(seed) if seed is not None else random.Random()
        self.team_codes = []
        for keywords, code_length in zip(keyword_cards, self.code_lengths):
            codes = list(permutations(range(len(keywords)), code_length))
            self.team_codes.append(codes)
    
    def __next__(self) -> tuple[Code, Code]:
        """Generate the next set of random codes for each team.

        Returns:
            tuple[Code, Code]: A tuple containing the randomly generated codes for each team.
        """
        return [self.random.choice(codes) for codes in self.team_codes]

    def __iter__(self):
        """Return the generator as an iterable object.

        Returns:
            RandomCodes: The generator object itself.
        """
        return self
    
class RandomKeywordCards:
    """Generator for generating random keyword cards for the Decrypto game.

    Args:
        card_lengths (Sequence[int], optional): The number of keywords on each team's keyword card. Defaults to DEFAULT_CARD_LENGTH.
        words (list[str], optional): The list of words to use for generating keyword cards. Defaults to the official English word list.
        seed (int, optional): The random seed for consistent card generation. Defaults to None.

    Yields:
        tuple[Keywords, Keywords]: A tuple containing the randomly generated keyword cards for each team.
    """
    def __init__(self, card_lengths: Sequence[int] = None, words: list[str] = english.words, seed: Optional[int] = None):
        self.card_lengths = card_lengths if card_lengths is not None else [DEFAULT_CARD_LENGTH] * 2
        self.words = words
        self.random = random.Random(seed) if seed is not None else random.Random()

    def __next__(self) -> tuple[Keywords, Keywords]:
        """Generate the next set of random keyword cards for each team.

        Returns:
            tuple[Keywords, Keywords]: A tuple containing the randomly generated keyword cards for each team.
        """
        word_indices = list(range(len(self.words)))
        cards = []
        for card_length in self.card_lengths:
            keyword_indices = []
            while len(keyword_indices) < card_length:
                keyword_index = self.random.choice(word_indices)
                word_indices.remove(keyword_index)
                keyword_indices.append(keyword_index)
            cards.append(tuple(self.words[i] for i in keyword_indices))
        return cards

    def __iter__(self):
        """Return the generator as an iterable object.

        Returns:
            RandomKeywordCards: The generator object itself.
        """
        return self