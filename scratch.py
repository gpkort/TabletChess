from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk
import pickle
from io import StringIO
import tkinter as tk

from GameManager import IMAGE_MAP, ChessGameManager
import chess
import chess.pgn
from chess import Board
from Display import SmartChessBoard
from Input import EventHandler, Event



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
    cb:SmartChessBoard = SmartChessBoard(canvas, IMAGE_MAP, show_algebraic=True)
    cgm:ChessGameManager = ChessGameManager(cb) 
    cgm.new_game()   
    root.update() 

    root.mainloop()
