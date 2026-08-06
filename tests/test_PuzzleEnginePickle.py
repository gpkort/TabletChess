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
    {"Pid" : 19, "PuzzleId" : "000rZ", "FEN": "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13", "Moves" : "d4e6 d6h2", "Rating" : 602, "GameUrl" : "https://lichess.org/seIMDWkD#25" },
    {"Pid" : 26, "PuzzleId" : "001KR", "FEN": "6Qk/p1p3pp/4N3/1p6/2q1r1n1/2B5/PP4PP/3R1R1K b - - 0 28", "Moves" : "h8g8 f1f8", "Rating" : 598, "GameUrl" : "https://lichess.org/TaT1Zl7z/black#56" },
    {"Pid" : 43, "PuzzleId" : "001wr", "FEN": "r4rk1/p3ppbp/Pp1q1np1/3PpbB1/2B5/2N5/1PPQ1PPP/3RR1K1 w - - 4 18", "Moves" : "f2f3 d6c5 g1h1 c5c4", "Rating" : 1067, "GameUrl" : "https://lichess.org/KnJ2mojX#35" },
    {"Pid" : 55, "PuzzleId" : "002Mm", "FEN": "rn1qr1k1/ppp3pQ/3p1pP1/3Pp3/2P1P3/8/PP3PP1/R1B1K3 b Q - 2 16", "Moves" : "g8f8 h7h8 f8e7 h8g7", "Rating" : 921, "GameUrl" : "https://lichess.org/wAkPv4uG/black#32" },
    {"Pid" : 57, "PuzzleId" : "002Q2", "FEN": "7k/p4R1p/3p3r/2pN1n2/2PbBBb1/3P2P1/P3r3/5R1K w - - 1 28", "Moves" : "f4h6 f5g3", "Rating" : 893, "GameUrl" : "https://lichess.org/yqAJ1jMv#55" },
]

TEST_THEME_MAP:list = [ 
    { "ThemeID":21, "PuzzleID":19}, { "ThemeID":60, "PuzzleID":19}, { "ThemeID":32, "PuzzleID":19},
    { "ThemeID":3, "PuzzleID":19}, { "ThemeID":10, "PuzzleID":19}, { "ThemeID":60, "PuzzleID":26},
    { "ThemeID":32, "PuzzleID":26}, { "ThemeID":63, "PuzzleID":26}, { "ThemeID":3, "PuzzleID":26},
    { "ThemeID":19, "PuzzleID":43}, { "ThemeID":54, "PuzzleID":43}, { "ThemeID":17, "PuzzleID":43},
    { "ThemeID":33, "PuzzleID":43}, { "ThemeID":63, "PuzzleID":43}, { "ThemeID":34, "PuzzleID":43},
    { "ThemeID":58, "PuzzleID":55}, { "ThemeID":60, "PuzzleID":55}, { "ThemeID":29, "PuzzleID":55},
    { "ThemeID":63, "PuzzleID":55}, { "ThemeID":34, "PuzzleID":55}, { "ThemeID":53, "PuzzleID":57},
    { "ThemeID":60, "PuzzleID":57}, { "ThemeID":32, "PuzzleID":57}, { "ThemeID":63, "PuzzleID":57},
    { "ThemeID":3, "PuzzleID":57}
]

TEST_DATAFRME:pd.DataFrame = pd.DataFrame( data= TEST_DATA )
TEST_THEME_MAP_DF:pd.DataFrame = pd.DataFrame( data= TEST_THEME_MAP )

class TestPuzzleEngineDataFrame:

    def test_init_with_df(self):
        gp:PuzzleEngineDF = PuzzleEngineDF(TEST_DATAFRME, TEST_THEME_MAP_DF)
        assert gp.get_puzzle_count() == 5

    def test_get_random(self):
        gp:PuzzleEngineDF = PuzzleEngineDF(TEST_DATAFRME, TEST_THEME_MAP_DF)
        pz:ActivityInfo = gp.get_random_puzzle()
        assert pz is not None
        idx:int = -1
        for i, p in enumerate(TEST_DATA):
            if pz.lichess_puzzle_id == p["PuzzleId"]:
                idx = i
                break

        assert idx != -1

    def test_random_moves(self):
        gp:PuzzleEngineDF = PuzzleEngineDF(TEST_DATAFRME, TEST_THEME_MAP_DF)
        pz:ActivityInfo = gp.get_random_puzzle()
        assert pz is not None
        pd:dict[str, Any] = {}
        for p in TEST_DATA:
            if pz.lichess_puzzle_id == p["PuzzleId"]:
                pd = p
                break

        assert len(pd.keys()) != 0
        assert pz.puzzle_moves is not None
        assert str(pd["Moves"]).split(" ") == pz.puzzle_moves

    def test_get_themes(self):
        gp:PuzzleEngineDF = PuzzleEngineDF(TEST_DATAFRME, TEST_THEME_MAP_DF)
        theme_ids:list[str] = []

        for t in TEST_THEME_MAP:
            if t["PuzzleID"] == 19:
                theme_ids.append(str(Theme(t["ThemeID"])))


        tbi:list[str] = gp.get_themes_by_id(19)
        assert sorted(theme_ids) == sorted(tbi)

    def test_random_themes(self):
            gp:PuzzleEngineDF = PuzzleEngineDF(TEST_DATAFRME, TEST_THEME_MAP_DF)
            pz:ActivityInfo = gp.get_random_puzzle()
            assert pz is not None

            theme_ids:list[str] = []
            id:int = -1

            for p in TEST_DATA:
                if pz.lichess_puzzle_id == p["PuzzleId"]:
                    id = p["Pid"]

            assert id != -1

            for t in TEST_THEME_MAP:
                if t["PuzzleID"] == id:
                    theme_ids.append(str(Theme(t["ThemeID"])))            
            
            tbi:list[str] = gp.get_themes_by_id(id)
            assert sorted(theme_ids) == sorted(tbi)