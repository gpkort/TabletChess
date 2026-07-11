from typing import Tuple
import sqlite3
import pandas as pd


from GameManager import STARTING_FEN, IMAGE_MAP
import chess
from chess import Board



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Puzzles.db"
PUZZLES_CSV:str = "lichess_db_puzzle.csv"



if __name__ == "__main__":
    print("start")
    board = Board()
    
    for rank in range(SQUARE_SIZE):
        row_str:str = ""
        for file in range(SQUARE_SIZE):     #-1, -1, -1):
            square = chess.square(file, 7-rank)
            name:str = chess.square_name(square)
            p:chess.Piece | None = board.piece_at(square)                # self.board.piece_map
            row_str += f"{name} ({rank},{file}): {"X" if p is None else p.symbol()}, "
        print(row_str)
