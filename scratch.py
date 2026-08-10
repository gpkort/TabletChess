from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk
import pickle
from io import StringIO

from GameManager import PuzzleEngineDF, ActivityInfo, Theme, create_openings_pickle
import chess
import chess.pgn
from chess import Board



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"
OPENING_BOOK = "komodo.bin"

CHUNK_SIZE = 200000




if __name__ == "__main__":
    create_openings_pickle("openings", 'openings.pkl')
    open_df:pd.DataFrame = pd.read_pickle('openings.pkl')
    
    print(open_df.head(5).to_dict('records'))
