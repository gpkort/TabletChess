from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk

from GameManager import STARTING_FEN, IMAGE_MAP
import chess
from chess import Board



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Puzzles.db"
PUZZLES_CSV:str = "lichess_db_puzzle.csv"

CHUNK_SIZE = 200000

def populate_themes(conn:Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT themes FROM Old_puzzles")
    ret:set[str] = set()

    rows = cursor.fetchall()
    for row in rows:
        themes:list[str] = str(row[0]).split(" ")
        for t in themes:
            ret.add(t)
    # cursor.close()
    
    inserts:list[Tuple[str]] = [(t,) for t in ret]
    # cursor = conn.cursor()
    cursor.executemany("INSERT INTO Theme (theme) VALUES (?)", inserts)
    
    conn.commit()
    cursor.close()

    return ret



if __name__ == "__main__":
    print("start")
    engine:Connection = connect(SQLITE_FILE)
    populate_themes(engine)

    themes:set[str] = populate_themes(engine)
    print(themes)
    # Theme
        
    # for chunk_df in pd.read_csv(PUZZLES_CSV, chunksize=CHUNK_SIZE):
    #     chunk_df.to_csv(path.join("puzzles", f"puzzle_{str(i)}.csv"), index=False)
    #     print(f"file {i} written")
    #     i+=1


