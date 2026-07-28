import pytest
import uuid
from dataclasses import fields, asdict

from chess import STARTING_FEN
import pandas as pd

from GameManager.game_data import GamePersisterDF, GameInfo, SaveOption, GamePersisterSaveException

TEST_FEN:str = "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13"

@pytest.fixture(scope="class")
def basic_games():
    """Provides a fresh, isolated dictionary of test data."""

    game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(GameInfo)])
    for i in range(5):
        game:GameInfo = GameInfo(id=str(uuid.uuid4()), game_name=f"game_{i}", FEN=STARTING_FEN,
                                white_player_name="white", black_player_name="black")
        puzzle:GameInfo = GameInfo(id=str(uuid.uuid4()), game_name=f"puzzle_{i}", FEN=STARTING_FEN,
                                        white_player_name="white", black_player_name="black", puzzle_id=f"puz_{i}")
        game_df = pd.concat([game_df, pd.DataFrame([asdict(game)]), pd.DataFrame([asdict(puzzle)])])    

    return game_df

@pytest.fixture(scope="class")
def full_games():
    """Provides a fresh, isolated dictionary of test data."""

    game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(GameInfo)])
    for i in range(7):
        game:GameInfo = GameInfo(id=str(uuid.uuid4()), game_name=f"game_{i}", FEN=STARTING_FEN,
                                white_player_name="white", black_player_name="black")
        game_df = pd.concat([game_df, pd.DataFrame([asdict(game)])])

    return game_df

@pytest.fixture(scope="class")
def full_puzzles():
    """Provides a fresh, isolated dictionary of test data."""

    game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(GameInfo)])
    for i in range(7):
        puzzle:GameInfo = GameInfo(id=str(uuid.uuid4()), game_name=f"puzzle_{i}", FEN=STARTING_FEN,
                                white_player_name="white", black_player_name="black", puzzle_id=f"puz_id_{i}")
        game_df = pd.concat([game_df, pd.DataFrame([asdict(puzzle)])])

    return game_df

@pytest.fixture(scope="class")
def full_both():
    game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(GameInfo)])
    for i in range(7):
        puzzle:GameInfo = GameInfo(id=str(uuid.uuid4()), game_name=f"puzzle_{i}", FEN=STARTING_FEN,
                                white_player_name="white", black_player_name="black", puzzle_id=f"puz_id_{i}")
        
        game:GameInfo = GameInfo(id=str(uuid.uuid4()), game_name=f"game_{i}", FEN=STARTING_FEN,
                                        white_player_name="white", black_player_name="black")
        game_df = pd.concat([game_df, pd.DataFrame([asdict(game)]), pd.DataFrame([asdict(puzzle)])])

    return game_df

class TestGamePersisterDF:
    def test_init_with_df(self, basic_games):
        gp:GamePersisterDF = GamePersisterDF(basic_games)
        assert len(gp.game_df) == 10
        assert len(gp.get_games()) == 5

    def test_init(self):
        gp:GamePersisterDF = GamePersisterDF(game_df=None)
        assert len(gp.game_df) == 0

    def test_game_count_game_only(self, full_games):
        gp:GamePersisterDF = GamePersisterDF(game_df=full_games)
        assert gp.game_count == 7
        assert gp.puzzle_count == 0

    def test_puzzle_count_puzzle_only(self, full_puzzles):
        gp:GamePersisterDF = GamePersisterDF(game_df=full_puzzles)
        assert gp.game_count == 0
        assert gp.puzzle_count == 7

    def test_mixed_count(self, basic_games):
        gp:GamePersisterDF = GamePersisterDF(game_df=basic_games)
        assert gp.game_count == 5
        assert gp.puzzle_count == 5

    def test_empty_count(self):
        gp:GamePersisterDF = GamePersisterDF(game_df=None)
        assert gp.game_count == 0
        assert gp.puzzle_count == 0

    def test_get_games_puzzles(self, basic_games):
        gp:GamePersisterDF = GamePersisterDF(game_df=basic_games)
        games:list[GameInfo] = gp.get_games()
        puzzles:list[GameInfo] = gp.get_puzzles()

        assert len([gi for gi in games if gi.puzzle_id is not None ]) == 0
        assert len([pz for pz in puzzles if pz.puzzle_id is None ]) == 0

    def test_save_game_with_room(self, basic_games):
        gp:GamePersisterDF = GamePersisterDF(game_df=basic_games)
        game_name:str = "test_save_game_with_room"
        game:GameInfo = GameInfo(game_name=game_name, FEN=TEST_FEN, white_player_name="w", black_player_name="b")

        assert gp.game_count == 5
        gp.save_data(game)
        assert gp.game_count == 6
        games:list[GameInfo] = gp.get_games()
        assert len([gi for gi in games if gi.game_name == game_name ]) == 1

    def test_save_game_no_room_no_overwrite(self, full_games):
        gp:GamePersisterDF = GamePersisterDF(game_df=full_games)
        game:GameInfo = GameInfo(game_name="blah", FEN=TEST_FEN, white_player_name="w", black_player_name="b")

        assert gp.game_count == 7
        with pytest.raises(GamePersisterSaveException):
            gp.save_data(game)

    def test_save_game_no_room_overwrite_first(self, full_games):
        gp:GamePersisterDF = GamePersisterDF(game_df=full_games)
        game_name:str = "overwrite_first"
        game:GameInfo = GameInfo(game_name=game_name, FEN=TEST_FEN, white_player_name="w", black_player_name="b")

        assert gp.game_count == 7
        assert any(g.game_name == "game_0" for g in gp.get_games())
        assert not any(g.game_name == game_name for g in gp.get_games())
        gp.save_data(game, SaveOption.OVERWRITE_FIRST)
        assert gp.game_count == 7
        assert not any(g.game_name == "game_0" for g in gp.get_games())
        assert any(g.game_name == game_name for g in gp.get_games())

    def test_save_game_no_room_overwrite_last(self, full_games):
            gp:GamePersisterDF = GamePersisterDF(game_df=full_games)
            game_name:str = "overwrite_first"
            game:GameInfo = GameInfo(game_name=game_name, FEN=TEST_FEN, white_player_name="w", black_player_name="b")
    
            assert gp.game_count == 7
            assert any(g.game_name == "game_6" for g in gp.get_games())
            assert not any(g.game_name == game_name for g in gp.get_games())
            gp.save_data(game, SaveOption.OVERWRITE_FIRST)
            assert gp.game_count == 7
            assert not any(g.game_name == "game_6" for g in gp.get_games())
            assert any(g.game_name == game_name for g in gp.get_games())
                
    


       
       

       
       
