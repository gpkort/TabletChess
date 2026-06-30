import chess
import chess.engine

class Game:
    """Chess Game controller"""

    def __init__(self, engine_path:str):
        self.engine_path = engine_path
    