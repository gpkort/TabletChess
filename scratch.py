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
    print(open_df.head())
    # open_df.drop(columns=['uci'], inplace=True)
    # # open_df.reset_index(drop=True, inplace=True)
    # print(open_df.columns)
    # # open_df["uci"] = [[] for _ in range(len(open_df))]
    # pgn:list[str] = open_df['pgn'].to_list()
    # ucis:list[list[str]] = []
    # board:Board = Board()


    # for p in pgn:
    #     game:chess.pgn.Game|None = chess.pgn.read_game(StringIO(str(p)))
    #     if game:
    #         ucis.append([m.uci() for m in game.mainline_moves()])

    # open_df["uci"] = ucis

    
    # print(open_df.head())
    # open_df.to_pickle('openings.pkl')

    # pe_db:PuzzleEngineDB = PuzzleEngineDB(connect(SQLITE_FILE))

    # pd.read

    # board:Board = Board()
    # mv:chess.Move = chess.Move.from_uci("e2e4")
    # board.push(mv)
    # with chess.polyglot.open_reader(OPENING_BOOK) as reader:
    #     for entry in reader.find_all(board):
    #         print(print(entry.move, entry.weight, entry.learn))
    




    

   


