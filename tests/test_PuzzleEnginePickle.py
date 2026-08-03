from dataclasses import fields, asdict
from typing import Any

import pytest
import pandas as pd


from GameManager import PuzzleEngineDF, ActivityInfo, Theme, DEFAULT_THEMES_DATAFRAME, PUZZLE_DATA_FIELDS

PUZZLES = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'London', 'Paris']
}

TEST_FEN:str = "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13"
TEST_MOVES:list[str] = ["d4e6", "d6h2"]
TEST_URL:str = "https://lichess.org/seIMDWkD#25"
TEST_THEMES:list[str] = [str(Theme.MATEIN1), str(Theme.MATEIN2), str(Theme.MATEIN3)]
TEST_DATA:list = [
    {"Pid" : 1, "PuzzleID" : "000rZ", "Fen": "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13", "Moves" : "d4e6 d6h2", "Rating" : 602, "GameUrl" : "https://lichess.org/seIMDWkD#25" },
    {"Pid" : 2, "PuzzleID" : "001KR", "Fen": "6Qk/p1p3pp/4N3/1p6/2q1r1n1/2B5/PP4PP/3R1R1K b - - 0 28", "Moves" : "h8g8 f1f8", "Rating" : 598, "GameUrl" : "https://lichess.org/TaT1Zl7z/black#56" },
    {"Pid" : 3, "PuzzleID" : "001wr", "Fen": "r4rk1/p3ppbp/Pp1q1np1/3PpbB1/2B5/2N5/1PPQ1PPP/3RR1K1 w - - 4 18", "Moves" : "f2f3 d6c5 g1h1 c5c4", "Rating" : 1067, "GameUrl" : "https://lichess.org/KnJ2mojX#35" },
    {"Pid" : 4, "PuzzleID" : "002Mm", "Fen": "rn1qr1k1/ppp3pQ/3p1pP1/3Pp3/2P1P3/8/PP3PP1/R1B1K3 b Q - 2 16", "Moves" : "g8f8 h7h8 f8e7 h8g7", "Rating" : 921, "GameUrl" : "https://lichess.org/wAkPv4uG/black#32" },
    {"Pid" : 5, "PuzzleID" : "002Q2", "Fen": "7k/p4R1p/3p3r/2pN1n2/2PbBBb1/3P2P1/P3r3/5R1K w - - 1 28", "Moves" : "f4h6 f5g3", "Rating" : 893, "GameUrl" : "https://lichess.org/yqAJ1jMv#55" },
]

TEST_DATAFRME:pd.DataFrame = pd.DataFrame( data= TEST_DATA )

@pytest.fixture(scope="class")
def basic_puzzles():
    """Provides a fresh, isolated dictionary of test data."""

    puzzle_df:pd.DataFrame = pd.DataFrame(data=None,columns=[PUZZLE_DATA_FIELDS])
    for i in range(10):
        activity:ActivityInfo = ActivityInfo(FEN=TEST_FEN, 
                                             lichess_puzzle_id=f"p_{i}",
                                             activity_name=f"a_{i}")
        puzzle_df = pd.concat([puzzle_df, pd.DataFrame([asdict(activity)])])

    return puzzle_df

class TestPuzzleEngineDataFrame:

    def test_init_with_df(self, basic_puzzles):
        gp:PuzzleEngineDF = PuzzleEngineDF(basic_puzzles, DEFAULT_THEMES_DATAFRAME)
        assert gp.get_puzzle_count() == 10

    def test_get_random(self, basic_puzzles):
        gp:PuzzleEngineDF = PuzzleEngineDF(TEST_DATAFRME, DEFAULT_THEMES_DATAFRAME)
        pz:ActivityInfo = gp.get_random_puzzle()
        assert pz is not None
            