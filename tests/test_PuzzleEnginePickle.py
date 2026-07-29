import pytest
import pandas as pd
from dataclasses import fields, asdict

from GameManager import PuzzleEngineDF, Puzzle, Theme, DEFAULT_THEMES_DATAFRAME

TEST_FEN:str = "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13"
TEST_MOVES:list[str] = ["d4e6", "d6h2"]
TEST_URL:str = "https://lichess.org/seIMDWkD#25"
TEST_THEMES:list[str] = [str(Theme.MATEIN1), str(Theme.MATEIN2), str(Theme.MATEIN3)]

@pytest.fixture(scope="class")
def basic_puzzles():
    """Provides a fresh, isolated dictionary of test data."""

    puzzle_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(Puzzle)])
    for i in range(10):
        puzzle:Puzzle = Puzzle(Pid=i, 
                               PuzzleId=f"p_{i}", 
                               FEN=TEST_FEN, Moves=TEST_MOVES, 
                               Rating=700, GameUrl=TEST_URL, themes=TEST_THEMES )
        puzzle_df = pd.concat([puzzle_df, pd.DataFrame([asdict(puzzle)])])    

    return puzzle_df

class TestPuzzleEngineDataFrame:

    def test_init_with_df(self, basic_puzzles):
        tdf:pd.DataFrame = pd.DataFrame([{"TID":t.value, "Theme": str(t)} for t in Theme])
        gp:PuzzleEngineDF = PuzzleEngineDF(basic_puzzles, DEFAULT_THEMES_DATAFRAME)
        assert gp.get_puzzle_count() == 10

    def test_get_random(self, basic_puzzles):
        gp:PuzzleEngineDF = PuzzleEngineDF(basic_puzzles, DEFAULT_THEMES_DATAFRAME)
        pz:Puzzle = gp.get_random_puzzle()
        assert pz is not None
            