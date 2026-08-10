import pytest
from typing import Any
from io import StringIO

import pandas as pd
import chess.pgn

from GameManager import OpeningLibrary, OpeningLibraryDF

OPENING_DATA:list[dict[str, Any]] = [
    {'eco': 'A00', 'name': 'Amar Opening', 'pgn': '1. Nh3', 'uci': ['g1h3'], 'game_hash': '6ac2e9c3a31bcfde278501f8c22b9b435452c77a27af0569001325f9bf95eb24'}, 
    {'eco': 'A00', 'name': 'Amar Opening: Paris Gambit', 'pgn': '1. Nh3 d5 2. g3 e5 3. f4', 'uci': ['g1h3', 'd7d5', 'g2g3', 'e7e5', 'f2f4'], 'game_hash': '7bbbc262c26e6127d54b60da354e2ba5d32a468df7c14a96f3e3f68721efb857'}, 
    {'eco': 'A00', 'name': 'Amar Opening: Paris Gambit, Gent Gambit', 'pgn': '1.Nh3 d5 2. g3 e5 3. f4 Bxh3 4. Bxh3 exf4 5. O-O fxg3 6. hxg3', 'uci': ['g1h3', 'd7d5', 'g2g3', 'e7e5', 'f2f4', 'c8h3', 'f1h3', 'e5f4', 'e1g1', 'f4g3', 'h2g3'], 'game_hash': '8a2ba57cca0f9f9653070f9cec971263966b44b8a89afeb390dd8808fc6eab39'}, 
    {'eco': 'A00', 'name': 'Amsterdam Attack', 'pgn': '1. e3 e5 2. c4 d6 3. Nc3 Nc6 4. b3 Nf6', 'uci': ['e2e3', 'e7e5', 'c2c4', 'd7d6', 'b1c3', 'b8c6', 'b2b3', 'g8f6'], 'game_hash': '2fb4ac6cfa57e5d0997383ee62972097d288df633ed023a2b2c554ab2587f4e2'}, 
    {'eco': 'A00', 'name': "Anderssen's Opening", 'pgn': '1. a3', 'uci': ['a2a3'], 'game_hash': 'df9ed462932746032d783a833445aae1fc1f9fd7ee1f08f50c08c81c55bab9ea'}
    ]

TEST_DF:pd.DataFrame = pd.DataFrame(data=OPENING_DATA)

class TestOpeningLibrary:
    """
    Unit tests for OpeningLibrary classes
    """
    def test_init(self):
        """
        Test for basic initialization
        """
        ol:OpeningLibraryDF = OpeningLibraryDF(TEST_DF)
        assert 5 == ol.openings_count

    def test_init_bad_df(self):
        """
        Test for non conformant name
        """
        df:pd.DataFrame = TEST_DF.copy()
        df = df.rename(columns={'eco': 'eco1'})
        with pytest.raises(ValueError):
            ol:OpeningLibraryDF = OpeningLibraryDF(df)  # pylint: disable=unused-variable

    def test_get_opening_name(self):
        """
        Test for getting opening name
        """
        ol:OpeningLibraryDF = OpeningLibraryDF(TEST_DF)
        
        gameo:list[str] = ['g1h3', 'd7d5', 'g2g3', 'e7e5', 'f2f4']
        gl:list[str] = []
        expected_name:str = 'Amar Opening: Paris Gambit'
        print(f"1 {hash(tuple(gameo))}")
        
        game:chess.pgn.Game|None = chess.pgn.read_game(StringIO(str(TEST_DF.iloc[1]['game_hash'])))
        if game:
            gl = [m.uci() for m in game.mainline_moves()]

        assert ol.get_opening_name(gameo) == expected_name
        
    def test_get_opening_name_bad(self):
        """
        Test for getting opening name with
        bad game
        """
        
        ol:OpeningLibraryDF = OpeningLibraryDF(TEST_DF)                
        game:list[str] = ['g1h3', 'd7d5', 'g2g3', 'e7e5', 'h2f4']
        
        assert ol.get_opening_name(game) is None
        
        
        
        
    