from sqlite3 import Connection, connect, Cursor
from typing import Tuple, Any, Hashable
from dataclasses import asdict


import pandas as pd

from .constants import Theme, Skill, SKILL_BUCKETS
from .utilites import PUZZLE_DATA_FIELDS, PuzzleEngine, ActivityInfo

PUZZLE_DB:str = "Light_Puzzles.db"
MIN_RATING:int = 399
DEFAULT_THEMES_DATAFRAME:pd.DataFrame = pd.DataFrame([{"TID":t.value, "Theme": str(t)} for t in Theme])

class PuzzleEngineDF(PuzzleEngine):
    """
    Puzzle engine that depends on pickle files
    Assumes puzzle_pickle contains:
        Pid, 
        PuzzleID, 
        Fen, 
        Moves, 
        Rating, 
        GameUrl

    """
    def __init__(self, 
                 puzzle_df:pd.DataFrame, 
                 theme_map_df:pd.DataFrame,*, 
                 shuffle_puzzles:bool=True) -> None:
        
        super().__init__()
        
        if "themes" not in list(puzzle_df.columns):            
            puzzle_df['themes'] = [[] for _ in range(len(puzzle_df))]

        if sorted(PUZZLE_DATA_FIELDS) != sorted(list(puzzle_df.columns)):
            raise ValueError("Incorrect format of puzzle_df.")

        if sorted(["ThemeID", "PuzzleID"]) != sorted(list(theme_map_df.columns)):
                            raise ValueError("Incorrect format of theme_map_df.")
        
        self.puzzle_df:pd.DataFrame = puzzle_df.copy()
        self.theme_map_df:pd.DataFrame = theme_map_df.copy()
        self.theme_df = DEFAULT_THEMES_DATAFRAME

        if shuffle_puzzles:
            self.puzzle_df.sample(frac=1).reset_index(drop=True, inplace=True)

    def get_puzzle_count(self)->int:
        return len(self.puzzle_df)

    def get_random_puzzle(self)->ActivityInfo:
        df_random = self.puzzle_df.sample(n=1)
        return(self._data_row_to_activity(df_random.iloc[0].to_dict()))

    def get_puzzles(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[ActivityInfo]:        
        filtered_df:pd.DataFrame = self.puzzle_df.copy()
        if themes is not None and len(themes) > 0:
            pids:set[int] = set()
            t_map:dict[Theme, list[int]] =  self.get_theme_to_puzzle_map(themes)
            for l in t_map.values():
                pids.update(l)
            filtered_df = self.puzzle_df[self.puzzle_df['Pid'].isin(pids)]
        if skill is not None:
            filtered_df = filtered_df[filtered_df['Rating'].between(SKILL_BUCKETS[skill][0], SKILL_BUCKETS[skill][1])]

        return [self._data_row_to_activity(row) for row in filtered_df.to_dict('records')]        #type: ignore
    
    def get_themes(self, *,filter:list[Theme]|None=None)->dict[Theme, str]:
        t_map:dict[Theme, str] = {}

        if filter is not None:
            t_map.update([(t, str(t)) for t in filter])
        else:
            t_map.update([(t.value, str(t)) for t in Theme])

        return t_map

    def get_theme_to_puzzle_map(self, themes:list[Theme]|None=None)->dict[Theme, list[int]]:
        t_map:dict[Theme, list[int]] = {}

        if themes is None or len(themes) == 0:
           themes = [Theme(int(t)) for t in self.theme_df["TID"].to_list()]

        for t in themes:
             df:pd.DataFrame = self.theme_map_df[self.theme_map_df["ThemeID"] == int(t.value)]
             t_map[t] = df["PuzzleID"].to_list()  
        
        return t_map

    def get_themes_by_id(self, pid:int)->list[str]:
        themes:list[str] = []
        # tids:pd.Series = self.theme_map_df.loc[self.theme_map_df["PuzzleID"] == pid, "ThemeID" ]
        df:pd.DataFrame = self.theme_map_df[self.theme_map_df["PuzzleID"] == pid] 

        for tid in df["ThemeID"].to_list():
             themes.append(str(Theme(int(tid))))

        return themes

    def _data_row_to_activity(self, row:dict[Hashable, Any]|dict[str, Any])->ActivityInfo:
        return ActivityInfo(
                    FEN=str(row["FEN"]),
                    lichess_puzzle_id=str(row["PuzzleId"]),
                    activity_name=str(row["PuzzleId"]),
                    puzzle_moves=str(row["Moves"]).split(" "),
                    puzzle_rating=int(row["Rating"]),
                    activity_url=str(row["GameUrl"]),
                    puzzle_themes=self.get_themes_by_id(int(row["Pid"]))
        
                )



