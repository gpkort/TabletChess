from sqlite3 import Connection, connect, Cursor
from typing import Tuple, Any


import pandas as pd

from .constants import Theme, Skill, SKILL_BUCKETS
from .utilites import Puzzle, PuzzleEngine

PUZZLE_DB:str = "Light_Puzzles.db"
MIN_RATING:int = 399

class PuzzleEnginePickel(PuzzleEngine):
    """
    Puzzle engine that depends on pikle files
    Assumes puzzle_pickle contains:
        Pid, 
        PuzzleID, 
        Fen, 
        Moves, 
        Rating, 
        GameUrl

    """
    def __init__(self, puzzle_pk_path:str, theme_pk_path:str,*, shuffle_puzzles:bool=True) -> None:
        super().__init__()
        self.puzzle_df:pd.DataFrame = pd.read_pickle(puzzle_pk_path)
        self.theme_map_df:pd.DataFrame = pd.read_pickle(theme_pk_path)

        print(len(self.puzzle_df))

        if shuffle_puzzles:
            self.puzzle_df.sample(frac=1).reset_index(drop=True, inplace=True)

    def get_puzzles(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[Puzzle]:
        filtered_df:pd.DataFrame = self.puzzle_df.copy()
        if themes is not None and len(themes) > 0:
            pids:set[int] = set()
            t_map:dict[Theme, list[int]] =  self.get_theme_to_puzzle_map(themes)
            for l in t_map.values():
                pids.update(l)
            filtered_df = self.puzzle_df[self.puzzle_df['PuzzleID'].isin(pids)]
        if skill is not None:
            filtered_df = filtered_df[filtered_df['Rating'].between(SKILL_BUCKETS[skill][0], SKILL_BUCKETS[skill][1])]

        return [Puzzle(**row) for row in filtered_df.to_dict('records')]        #type: ignore

    
    def get_themes(self, *,filter:list[Theme]|None=None)->dict[Theme, str]:
        t_map:dict[Theme, str] = {}

        if filter is not None:
            t_map.update([(t, str(t)) for t in filter])
        else:
            t_map.update([(t.value, str(t)) for t in Theme])

        return t_map

    def get_theme_to_puzzle_map(self, themes:list[Theme]|None=None)->dict[Theme, list[int]]:
        t_df:pd.DataFrame = pd.DataFrame()
        t_map:dict[Theme, list[int]] = {}

        if themes is not None and len(themes) > 0:
            t_df = self.theme_map_df[self.theme_map_df['ThemeID'].isin(themes)]
        else:
            t_df = self.theme_map_df

        for k, v in t_df.to_dict().items():
            if t_map.get(Theme(k)) is None:        
                t_map[Theme(k)] = []
            t_map[Theme(k)].append(int(v))
        
        return t_map

class PuzzleEngineDB(PuzzleEngine):
    def __init__(self, connection:Connection):
        super().__init__()
        self._connection:Connection = connection

    def get_puzzles(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[Puzzle]:
        puzzles:list[Puzzle]= []
        rows:list[Any] = self.get_puzzle_rows(self.get_puzzles_query(themes, skill, limit))
        for row in rows:
            puzzles.append(self.get_puzzle_from_row(row))

        return puzzles

    def get_theme_to_puzzle_map(self, themes:list[Theme]|None=None)->dict[Theme, list[int]]:
       
        query:str = f"SELECT ThemeID, PuzzleId FROM ThemeMap"
        theme_map:dict[Theme, list[int]] = {}
        if themes is not None:
            t_names:list[str] = [f"'{str(t)}'" for t in themes]
            query += f"WHERE ThemeId IN ({",".join([str(int(i)) for i in themes])})"        #type: ignore
        query += ";"

        ids:list[Any] = self.get_puzzle_rows(query)
       
        for id in ids:
            has_list:list[int]|None = theme_map.get(id[0])
            if has_list is None:
                theme_map[Theme(int(id[0]))] = []       
            theme_map[Theme(int(id[0]))].append(int(id[1]))    

        return theme_map
   
    def get_themes(self, *,filter:list[Theme]|None=None)->dict[Theme, str]:
        themes:dict[Theme, str] = {}
        query:str = "SELECT TID, theme FROM Theme"

        if filter:
            query += f" WHERE Theme LIKE '%{filter}%'"
        query += ";"

        rows:list[Any] = self.get_puzzle_rows(query)
        for row in rows:
            themes[row[0]] = row[1]

        return themes


    def get_puzzle_from_row(self, row:Any)->Puzzle:
        """
        turn a row return from a query 
        SELECT Pid, PuzzleID, Fen, Moves, Rating FROM Old_Puzzles
        int Puzzle object

        Args:
        row: row[0]=id, row[1]=puzzle_id, row[2]=fen, row[3]=moves, row[4]=rating, row[5]=GameUrl
        """
        moves:list[str] = str(row[3]).split(" ")
        return Puzzle(Pid=int(row[0]), 
                      PuzzleId=str(row[1]), 
                      FEN=str(row[2]), 
                      Moves=moves,
                      Rating=row[4],
                      GameUrl=row[5])
    
    def get_puzzle_rows(self, query:str)->list[Any]:
        cursor:Cursor = self._connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        return rows
    
    def get_puzzles_query(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->str:
        query:str = "SELECT Pid, PuzzleID, Fen, Moves, Rating, GameUrl FROM Old_Puzzles"
        
        if themes is not None:            
            tids:dict[Theme, str] = self.get_themes(filter=themes)
            query += f" WHERE PID IN ({" ,".join([str(i) for i in tids.keys()])})"  
        if skill is not None:
            stm:str = " AND" if themes is not None else " WHERE"
            query += stm + f" Rating >= {SKILL_BUCKETS[skill][0]} AND Rating <= {SKILL_BUCKETS[skill][1]}"
        if limit > 0:
            query += f" LIMIT {str(limit)}"
        
        return query + ";"

# if __name__ == "__main__":    
#     pe_db:PuzzleEngineDB = PuzzleEngineDB(connect(PUZZLE_DB))
#     pe_pk:PuzzleEnginePickel = PuzzleEnginePickel("puzzle_pk", "theme_pk")



