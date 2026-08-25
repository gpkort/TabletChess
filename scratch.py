from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk
import pickle
from io import StringIO
import tkinter as tk

from GameManager import IMAGE_MAP, ChessGameManager, GameConfiguration
from chess import Board, engine
from Display import SmartChessBoard
from Input import EventHandler, Event



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"
OPENING_BOOK = "komodo.bin"
ENGINE_PATH:str = "stockfish-windows-x86-64-avx2.exe"
CHUNK_SIZE = 200000


chess_engine:engine.SimpleEngine = engine.SimpleEngine.popen_uci(ENGINE_PATH)
root = tk.Tk()
root.title("Chess")


def on_closing():
        """
        Callback from close root frame
        """
        chess_engine.close()
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)


if __name__ == "__main__":    
    
    canvas:tk.Canvas = tk.Canvas(root, width=480, height=480)
    canvas.pack(fill="both", expand=True)
    cb:SmartChessBoard = SmartChessBoard(canvas, IMAGE_MAP, show_algebraic=True)
    cgm:ChessGameManager = ChessGameManager(cb, chess_engine) 
    cgm.load_game(GameConfiguration.fromJson("{}"))   
    root.update() 

    root.mainloop()
