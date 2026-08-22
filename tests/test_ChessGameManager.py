import pytest
import uuid
import json

from chess import STARTING_FEN, WHITE, BLACK

from GameManager import GameConfiguration

TEST_FEN:str = "2kr1b1r/p1p2pp1/2pqb3/7p/3N2n1/2NPB3/PPP2PPP/R2Q1RK1 w - - 2 13"

# TEST_JSON:str = "{""id"":None,""name"":""GAME""," 


class TestGameConfiguration:
    """Unit tests for activity
    """
    # pylint: disable=redefined-outer-name
    def test_from_json(self):
        gc:GameConfiguration = GameConfiguration.fromJson("{}")
        assert gc is not None
        assert gc.name is not None
        assert gc.name.startswith("game_")
        assert gc.fen == STARTING_FEN
        assert len(gc.move_stack) == 0
        assert gc.player_1_color == WHITE
        assert gc.player_2_color == BLACK
        assert gc.player_1_name == "Player 1"
        assert gc.player_2_name == "Player 2"
        assert gc.engine_path is None
        assert gc.engine_elo == 1100

