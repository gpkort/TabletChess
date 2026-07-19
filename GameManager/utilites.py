from sqlite3 import Connection
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Tuple

import pandas as pd

from .constants import Theme, Skill, SKILL_BUCKETS

@dataclass
class Puzzle:
    """
    Dataclass for puzzle information
    """
    Pid:int
    PuzzleId:str
    FEN:str
    Moves:list[str]
    Rating:int
    GameUrl:str
    themes:list[str] = field(default_factory=list)


class PuzzleEngine(ABC):
    """
    Abstract method for puzzle engines

    Args:
        ABC (_type_): _description_
    """
    @abstractmethod
    def get_puzzles(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[Puzzle]:
        pass
    
    @abstractmethod
    def get_themes(self, *,filter:list[Theme]|None=None)->dict[Theme, str]:
        pass

    @abstractmethod
    def get_theme_to_puzzle_map(self, themes:list[Theme]|None=None)->dict[Theme, list[int]]:
        pass


def create_puzzle_pickle(connection:Connection, 
                         puzzle_pickle_path:str,
                         theme_pickle_path: str,
                         sample_size:int = 5000,
                         themes:list[Theme]|None=None, 
                         skill:Skill|None=None):
    """
    Create a pickle file from database

    Args:
        connection (Connection): _description_
        puzzle_pickle_path (str): _description_
        theme_pickle_path (str): _description_
        sample_size (int, optional): _description_. Defaults to 5000.
        themes (list[Theme] | None, optional): _description_. Defaults to None.
        skill (Skill | None, optional): _description_. Defaults to None.
    """
    query:str = "SELECT Pid, PuzzleID, Fen, Moves, Rating, GameUrl FROM Old_Puzzles"
        
    if themes is not None:            
        tids:list[int] = [t.id for t in themes]             #type: ignore

        query += f" WHERE PID IN ({" ,".join([str(i) for i in tids])})"  
    if skill is not None:
        stm:str = " AND" if themes is not None else " WHERE"
        query += stm + f" Rating >= {SKILL_BUCKETS[skill][0]} AND Rating <= {SKILL_BUCKETS[skill][1]}"
    
    puz_df:pd.DataFrame = pd.read_sql_query(query, connection)
    num_to_drop:int = len(puz_df) - sample_size
    print(num_to_drop)
    if num_to_drop > 0:
        puz_df.drop(puz_df.sample(n=num_to_drop).index, inplace=True)

    ids:list[int] = puz_df["Pid"].to_list()

    query = f"SELECT ThemeID, PuzzleID FROM ThemeMap WHERE PuzzleID IN ({",".join([str(i) for i in ids])});"
    th_df:pd.DataFrame = pd.read_sql_query(query, connection)

    puz_df.to_pickle(puzzle_pickle_path)
    th_df.to_pickle(theme_pickle_path)

def create_themes_pickle(self, connection:Connection, pickle_path:str):
    df:pd.DataFrame = pd.read_sql_query("SELECT TID, theme FROM Theme", connection)
    df.to_pickle(pickle_path)






