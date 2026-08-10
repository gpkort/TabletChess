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
from Display import ChessBoard



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"
OPENING_BOOK = "komodo.bin"

CHUNK_SIZE = 200000




if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")
    root.geometry("480x600")
    # frame:tk.Frame = tk.Frame(root, width=480, height=600)
    # frame.pack(fill="both", expand=True)
    canvas:tk.Canvas = tk.Canvas(root, width=480, height=180,  borderwidth=5)
    canvas.pack(fill="both", expand=True)
    ChessBoard(canvas, IMAGE_MAP)
    # frame.update()
    root.update() 

    root.mainloop()
