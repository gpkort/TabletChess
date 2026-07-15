from typing import Tuple, Any
from sqlite3 import connect, Connection, Cursor
import pandas as pd
from os import path, walk

from GameManager import STARTING_FEN, IMAGE_MAP, create_puzzle_pickle
import chess
from chess import Board



SQUARE_SIZE:int = 8
SQLITE_FILE:str = "Light_Puzzles.db"
PUZZLES_CSV:str = "lichess_db_puzzle.csv"

CHUNK_SIZE = 200000

def populate_themes(conn:Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT themes FROM Old_puzzles;")
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

def populate_map(conn:Connection):
    cursor = conn.cursor()
    theme_map:list[Tuple[int, int]] = []

    cursor.execute("SELECT PID, themes FROM Old_puzzles;")
    rows = cursor.fetchall()

    for row in rows:        
        pid:int = row[0]

        if pid % 1000 == 0:
            print(f"Row: {pid}")
        themes:list[Tuple[str]] = [(t,) for t in str(row[1]).split(" ")]
        for t in themes:
            cursor.execute("SELECT TID  FROM Theme WHERE theme = ?;", t)
            res = cursor.fetchall()
            theme_map.append((res[0][0], pid))

    cursor.executemany("INSERT INTO ThemeMap (ThemeID, PuzzleID) VALUES (?,?)", theme_map)



    conn.commit()
    cursor.close()

    print(theme_map[:50])


if __name__ == "__main__":
    print("start")
    vals:list[int] = [1,2,3,4,5]
    print(", ".join([str(i) for i in vals]))

    create_puzzle_pickle(connect(SQLITE_FILE), "puzzle.pk", "theme_pk")

    # sq:list[chess.SQUARES]
        
    # for chunk_df in pd.read_csv(PUZZLES_CSV, chunksize=CHUNK_SIZE):
    #     chunk_df.to_csv(path.join("puzzles", f"puzzle_{str(i)}.csv"), index=False)
    #     print(f"file {i} written")
    #     i+=1


