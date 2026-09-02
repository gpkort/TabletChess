# pylint: disable=missing-module-docstring
import sys
from typing import Any
# from sqlite3 import connect, Connection, Cursor
# import pandas as pd
# from os import path, walk
# import pickle
# from io import StringIO
# import tkinter as tk

import chess
from chess import engine, Board

from GameManager import IMAGE_MAP, ChessGameManager, ChessCoach
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


# chess_engine:engine.SimpleEngine = engine.SimpleEngine.popen_uci(ENGINE_PATH)

def on_closing(_:Event, __:dict[str, Any]):
    """
    Callback from close root frame
    """
    # chess_engine.close()
    sys.exit(0)

if __name__ == "__main__":
    cb:Board = Board("3qkbnr/pp2pp1p/6p1/3p4/B7/7P/PPPPPPP1/RN1QKBNR w - - 0 1")
    print(ChessCoach.get_legal_moves(cb.copy(), chess.BLACK))


    # cu:ChessUI = ChessUI(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH-40)
    # cb:SmartChessBoard = SmartChessBoard(cu.canvas, IMAGE_MAP, show_algebraic=True)
    # cgm:ChessGameManager = ChessGameManager(cb, cu, chess_engine, single_player=False)

    # cu.register_handler(EventHandler(Event.QUIT, on_closing))
    # cu.start()
