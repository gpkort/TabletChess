from chess import Board

from .constants import STARTING_FEN
from Input import EventDispatcher, EventHandler

class ChessManager:
    def __init__(self):
        self.board = Board()
        print(self.board)
        
    def start(self):
        self.board.reset()
        
    def legal_moves(self)->list:
        ...
    def legal_moves_by_square(self, str)->list:
        print(self.board.legal_moves)
        return []