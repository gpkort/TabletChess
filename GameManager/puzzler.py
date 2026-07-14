from sqlite3 import Connection, connect, Cursor
from typing import Tuple, Any
from dataclasses import dataclass, field

from constants import Theme, Skill, SKILL_BUCKETS

PUZZLE_DB:str = "Light_Puzzles.db"
MIN_RATING:int = 399


@dataclass
class Puzzle:
    id:int
    puzzle_id:str
    fen:str
    first_move:str
    solutions:list[str]
    rating:int
    themes:list[str] = field(default_factory=list)

class Puzzle_Engine:
    def __init__(self, connection:Connection):
        self._connection:Connection = connection

    def get_puzzles(self, themes:Theme|list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[Puzzle]:
        puzzles:list[Puzzle]= []
        cursor:Cursor = self._connection.cursor()
        query:str = "SELECT Pid, PuzzleID, Fen, Moves, Rating FROM Old_Puzzles"
        
        if themes is not None:            
            tids:list[int] = self.get_puzzle_id_by_themes(themes)
            query += f" WHERE PID IN ({" ,".join([str(i) for i in tids])})"  
        if skill is not None:
            stm:str = " AND" if themes is not None else " WHERE"
            query += stm + f" Rating >= {SKILL_BUCKETS[skill][0]} AND Rating <= {SKILL_BUCKETS[skill][1]}"
        if limit > 0:
            query += f" LIMIT {str(limit)}"
        query += ";"
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            puzzles.append(self.get_puzzle_from_row(row))

        cursor.close()
        
        return puzzles

    def get_puzzle_id_by_themes(self, themes:Theme|list[Theme])->list[int]:
        if type(themes) is Theme: 
            themes = [themes]               
        t_names:list[str] = [f"'{str(t)}'" for t in themes]          

        query_id:str = f"SELECT PuzzleId FROM ThemeMap WHERE ThemeId IN (SELECT TID FROM Theme WHERE theme IN ({", ".join(t_names)}))"
        
        cursor:Cursor = self._connection.cursor()
        cursor.execute(query_id)
        ids = cursor.fetchall()
        id_vals:list[int] = [int(id[0]) for id in ids]
        cursor.close()

        return id_vals

    
    def get_themes_by_name(self, *,filter:str|None=None)->list[Tuple[int, str]]:
        themes:list[Tuple[int, str]] = []

        cursor:Cursor = self._connection.cursor()
        query:str = "SELECT TID, theme FROM Theme"

        if filter:
            query += f" WHERE Theme LIKE '%{filter}%'"

        query += ";"
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()

        for row in rows:
            themes.append((row[0], row[1]))

        return themes
    
    def get_puzzle_from_row(self, row:Any)->Puzzle:
        """
        turn a row return from a query 
        SELECT Pid, PuzzleID, Fen, Moves, Rating FROM Old_Puzzles
        int Puzzle object

        Args:
        row: row[0]=id, row[1]=puzzle_id, row[2]=fen, row[3]=moves, row[4]=rating
        """
        moves:list[str] = str(row[3]).split(" ")
        return Puzzle(int(row[0]), str(row[1]), str(row[2]), moves[0], moves[1:], int(row[4]))


# if __name__ == "__main__":
#     pe:Puzzle_Engine = Puzzle_Engine(connect(PUZZLE_DB))

    



