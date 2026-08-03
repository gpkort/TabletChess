import pytest
import uuid
from dataclasses import fields, asdict

from chess import STARTING_FEN
import pandas as pd

from GameManager.game_data import ActivityPersisterDF, ActivityInfo, SaveOption, ActivityPersisterSaveException

TEST_FEN:str = "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13"

@pytest.fixture(scope="class")
def basic_activities():
    """Provides a fresh, isolated dictionary of test data."""

    game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(ActivityInfo)])
    for i in range(10):
        activity:ActivityInfo = ActivityInfo(activity_name=f"activity_{i}",
                                             FEN=STARTING_FEN,
                                             activity_id=uuid.uuid4())
        game_df = pd.concat([game_df, pd.DataFrame([asdict(activity)])])

    return game_df

@pytest.fixture(scope="class")
def full_activities():
    """Provides a fresh, isolated dictionary of test data."""

    game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(ActivityInfo)])
    for i in range(15):
        activity:ActivityInfo = ActivityInfo(activity_name=f"activity_{i}",
                                                     FEN=STARTING_FEN,
                                                     activity_id=uuid.uuid4())
        game_df = pd.concat([game_df, pd.DataFrame([asdict(activity)])])

    return game_df


class TestActivityPersisterDF:
    """Unit tests for activity
    """
    def test_init_with_df(self, basic_activities):
        gp:ActivityPersisterDF = ActivityPersisterDF(basic_activities)
        assert gp.activity_count == 10

    def test_init(self):
        gp:ActivityPersisterDF = ActivityPersisterDF(activity_df=None)
        assert gp.activity_count == 0
   
    def test_get_games_puzzles(self, basic_activities):
        gp:ActivityPersisterDF = ActivityPersisterDF(activity_df=basic_activities)
        activities:list[ActivityInfo] = gp.get_activities()

        assert len(activities) == gp.activity_count

    def test_save_game_with_room(self, basic_activities):
        gp:ActivityPersisterDF = ActivityPersisterDF(activity_df=basic_activities)
        game_name:str = "test_save_game_with_room"
        activity:ActivityInfo = ActivityInfo(activity_name=game_name,
                                                     FEN=STARTING_FEN,
                                                     activity_id=uuid.uuid4())

        assert gp.activity_count == 10
        gp.save_activity(activity, SaveOption.NO_OVERWITE)
        assert gp.activity_count == 11
        games:list[ActivityInfo] = gp.get_activities()
        assert len([gi for gi in games if gi.activity_name == game_name ]) == 1

    def test_save_game_no_room_no_overwrite(self, full_activities):
        gp:ActivityPersisterDF = ActivityPersisterDF(activity_df=full_activities)
        activity:ActivityInfo = ActivityInfo(activity_name="game_name",
                                                             FEN=STARTING_FEN,
                                                             activity_id=uuid.uuid4())

        assert gp.activity_count == 15
        with pytest.raises(ActivityPersisterSaveException):
            gp.save_activity(activity, SaveOption.NO_OVERWITE)

    def test_save_game_no_room_overwrite_first(self, full_activities):
        gp:ActivityPersisterDF = ActivityPersisterDF(activity_df=full_activities)
        game_name:str = "overwrite_first"
        activity:ActivityInfo = ActivityInfo(activity_name=game_name,
                                            FEN=STARTING_FEN,white_player_name="w", black_player_name="b")

        assert gp.activity_count == 15
        assert any(g.activity_name == "activity_0" for g in gp.get_activities())
        assert not any(g.activity_name == game_name for g in gp.get_activities())
        gp.save_activity(activity, SaveOption.OVERWRITE_FIRST)
        assert gp.activity_count == 15
        assert not any(g.activity_name == "activity_0" for g in gp.get_activities())
        assert any(g.activity_name == game_name for g in gp.get_activities())

    def test_save_game_no_room_overwrite_last(self, full_activities):
        gp:ActivityPersisterDF = ActivityPersisterDF(activity_df=full_activities)
        game_name:str = "overwrite_first"
        activity:ActivityInfo = ActivityInfo(activity_name=game_name,
                                            FEN=STARTING_FEN,white_player_name="w", black_player_name="b")

        assert gp.activity_count == 15
        assert any(g.activity_name == "activity_14" for g in gp.get_activities())
        assert not any(g.activity_name == game_name for g in gp.get_activities())
        gp.save_activity(activity, SaveOption.OVERWRITE_LAST)
        assert gp.activity_count == 15
        assert not any(g.activity_name == "activity_14" for g in gp.get_activities())
        assert any(g.activity_name == game_name for g in gp.get_activities())
            
                
    


       
       

       
       
