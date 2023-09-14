import pytest
from decryptogame.generators import RandomKeywordCards, RandomCodes

@pytest.fixture
def keyword_cards():
    return [("a", "b", "c", "d"), ("e", "f", "g", "h")]
    
class TestRandomKeywordCards:
    def test_default(self):
        card_generator = RandomKeywordCards()
        card1, card2 = next(card_generator)

        assert len(card1) == 4
        assert len(card2) == 4

        assert len(set(card1)) == 4
        assert len(set(card2)) == 4

    def test_seed(self):
        cards1 = next(RandomKeywordCards(seed=400))
        cards2 = next(RandomKeywordCards(seed=400))
        print(cards1, cards2)
        assert cards1 == cards2

class TestRandomCodes:
    def test_default(self, keyword_cards):
        code1, code2 = next(RandomCodes(keyword_cards))

        assert len(code1) == 3
        assert len(code2) == 3

        assert len(set(code1)) == 3
        assert len(set(code2)) == 3

        assert all(code_num in range(4) for code_num in code1)
        assert all(code_num in range(4) for code_num in code2)

    def test_seed(self, keyword_cards):
        codes1 = next(RandomCodes(keyword_cards, seed=400))
        codes2 = next(RandomCodes(keyword_cards, seed=400))

        assert codes1 == codes2


        