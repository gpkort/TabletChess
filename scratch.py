from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk
import pickle
from io import StringIO
import tkinter as tk

from GameManager import IMAGE_MAP, ActivityInfo, Theme, create_openings_pickle
import chess
import chess.pgn
from chess import Board
from Display import ChessBoard, ChessBoardInfo



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"
OPENING_BOOK = "komodo.bin"

CHUNK_SIZE = 200000


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")    
    canvas:tk.Canvas = tk.Canvas(root, width=480, height=480)
    canvas.pack(fill="both", expand=True)
    cb:ChessBoard = ChessBoard(canvas, IMAGE_MAP)
    bi:ChessBoardInfo = ChessBoardInfo(selected_square=chess.B3,
                                       previous_square=chess.H8, target_square=chess.H1,
                                       legal_squares=[s for s in range(40,48)],
                                       piece_location={chess.A4:"p", 
                                                       chess.B4:"P",
                                                       chess.C4:"k",
                                                       chess.D4:"K",
                                                       chess.E4:"q",
                                                       chess.F4:"Q"})
    
    cb.update_board_display(bi)
    cb.show_algebraic(True)
    
    root.update() 

    root.mainloop()
