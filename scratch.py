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
from Input import EventHandler, Event, ChessUI



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"
OPENING_BOOK = "komodo.bin"
ENGINE_PATH:str = "stockfish-windows-x86-64-avx2.exe"
CHUNK_SIZE = 200000
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
# SCREEN_WIDTH = 1024
# SCREEN_HEIGHT = 768


chess_engine:engine.SimpleEngine = engine.SimpleEngine.popen_uci(ENGINE_PATH)

def on_closing(ev:Event, data:dict[str, Any]):
        """
        Callback from close root frame
        """
        chess_engine.close()
        exit(0)

if __name__ == "__main__":    
    chess_ui:ChessUI = ChessUI(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH-40)    
    cb:SmartChessBoard = SmartChessBoard(chess_ui.canvas, IMAGE_MAP, show_algebraic=True)
    cgm:ChessGameManager = ChessGameManager(cb, chess_ui.widget_frame, chess_engine)

    chess_ui.register_handler(EventHandler(Event.QUIT, on_closing))
    chess_ui.start()
     
    
