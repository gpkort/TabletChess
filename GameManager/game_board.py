from chess import Board

from .constants import STARTING_FEN
from Input import EventDispatcher, EventHandler

class MyBoard(Board, EventDispatcher):
    def __init__(self, fen:str|None=STARTING_FEN):
        super().__init__(fen)