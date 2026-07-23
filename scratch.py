from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk

from GameManager import PuzzleEnginePickel, Puzzle, Theme
import chess
from chess import Board



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"

CHUNK_SIZE = 200000




if __name__ == "__main__":
    # pe_db:PuzzleEngineDB = PuzzleEngineDB(connect(SQLITE_FILE))
    pe_pk:PuzzleEnginePickel = PuzzleEnginePickel(path.join(PICKLE_DIR, "puzzle_pk"), path.join(PICKLE_DIR,"theme_pk"))

    # puzzle_db:list[Puzzle] = pe_db.get_puzzles()
    puzzle_pk:list[Puzzle] = pe_pk.get_puzzles()

    # print(f"DB: {len(puzzle_db)}, PK: {len(puzzle_pk)}")

    # puz_db:list[int] = [p.Pid for p in puzzle_db]
    puz_pk:list[int] = [p.Pid for p in puzzle_pk]
    pk_map:dict[Theme, list[int]] = pe_pk.get_theme_to_puzzle_map([Theme.MATEIN1, Theme.MATEIN2])
    ids:set[int] = set()
    ids.update(pk_map[Theme.MATEIN1])
    ids.update(pk_map[Theme.MATEIN2])
    puzzle_pk = pe_pk.get_puzzles(themes=[Theme.MATEIN1, Theme.MATEIN2])

    print(f"map: {len(ids)}")
    print(f"puz: {len(puzzle_pk)}")

   


