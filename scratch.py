from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk

from GameManager import PuzzleEngineDB, PuzzleEnginePickel, Puzzle
import chess
from chess import Board



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"

CHUNK_SIZE = 200000




if __name__ == "__main__":
    pe_db:PuzzleEngineDB = PuzzleEngineDB(connect(SQLITE_FILE))
    pe_pk:PuzzleEnginePickel = PuzzleEnginePickel(path.join(PICKLE_DIR, "puzzle_pk"), path.join(PICKLE_DIR,"theme_pk"))

    puzzle_db:list[Puzzle] = pe_db.get_puzzles()
    puzzle_pk:list[Puzzle] = pe_pk.get_puzzles()

    print(f"DB: {len(puzzle_db)}, PK: {len(puzzle_pk)}")

    puz_db:list[int] = [p.Pid for p in puzzle_db]
    puz_pk:list[int] = [p.Pid for p in puzzle_pk]

    for i in puz_pk:
        if not i in puz_db:
            print(f"Puzzle ({i}) is missing")

    # def get_puzzles(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[Puzzle]    
    # def get_themes(self, *,filter:list[Theme]|None=None)->dict[Theme, str]
    # def get_theme_to_puzzle_map(self, themes:list[Theme]|None=None)->dict[Theme, list[int]]:

    # for chunk_df in pd.read_csv(PUZZLES_CSV, chunksize=CHUNK_SIZE):
    #     chunk_df.to_csv(path.join("puzzles", f"puzzle_{str(i)}.csv"), index=False)
    #     print(f"file {i} written")
    #     i+=1


