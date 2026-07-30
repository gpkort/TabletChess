from sqlite3 import Connection
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Any, Tuple
import uuid

import pandas as pd
from chess import Outcome

from .constants import Theme, Skill, SKILL_BUCKETS

class ActivityStatus(Enum):
    UNKNOWN = 0
    NOT_STARTED = 1
    IN_PROGRESS = 2
    COMPLETE = 3


class ActivityPersisterSaveException(Exception):
    pass

@dataclass
class ActivityInfo:        
    FEN:str
    activity_name:str
    activity_id:uuid.UUID | None = None
    lichess_puzzle_id:str|None=None
    puzzle_moves:list[str]|None = None
    puzzle_rating:int|None = None
    activity_url:str|None = None
    puzzle_themes:list[str] = field(default_factory=list)
    white_player_name:str = "white"
    black_player_name:str = "black"
    game_engine_file:str|None = None
    activity_moves:list[str] = field(default_factory=list)
    activity_outcome:Outcome|None = None
    activity_status:ActivityStatus = ActivityStatus.UNKNOWN

PUZZLE_DATA_FIELDS:list[str] = ["Pid", "PuzzleID", "Fen", "Moves", "Rating", "GameUrl", "themes"]
# @dataclass
# class Puzzle:
#     """
#     Dataclass for puzzle information
#     """
#     Pid:int
#     PuzzleId:str
#     FEN:str
#     Moves:list[str]
#     Rating:int
#     GameUrl:str
#     themes:list[str] = field(default_factory=list)

# @dataclass
# class GameInfo:
#     """
#     Data class games being played or saved
#     """
        
#     FEN:str
#     game_name:str
#     white_player_name:str
#     black_player_name:str
#     game_engine_file:str|None = None
#     puzzle_id:str|None = None
#     id:str|None = None    

class PuzzleEngine(ABC):
    """
    Abstract method for puzzle engines

    Args:
        ABC (_type_): _description_
    """
    @abstractmethod
    def get_puzzle_count(self)->int:
        pass

    @abstractmethod
    def get_random_puzzle(self)->ActivityInfo:
        pass

    @abstractmethod
    def get_puzzles(self, themes:list[Theme]|None=None, skill:Skill|None=None, limit:int=0)->list[ActivityInfo]:
        pass
        
    @abstractmethod
    def get_themes(self, *,filter:list[Theme]|None=None)->dict[Theme, str]:
        pass

    @abstractmethod
    def get_theme_to_puzzle_map(self, themes:list[Theme]|None=None)->dict[Theme, list[int]]:
        pass

class SaveOption(Enum):
    NO_OVERWITE = 0
    OVERWRITE_LAST = 1
    OVERWRITE_FIRST = 2

class ActivityPersister(ABC):
    def __init__(self, *, max_activity_save:int):
        self._max_activity_save = max_activity_save

        self._activity_count:int = 0

    @property
    def activity_count(self)->int:
        return self._activity_count

    
    @property
    def max_activity_save(self)->int:
        return self._max_activity_save
    @max_activity_save.setter
    def max_game_save(self, value:int):
        self._max_activity_save = value

    @abstractmethod
    def save_activity(self, activity:ActivityInfo, save_option:SaveOption=SaveOption.NO_OVERWITE):
        ...

    @abstractmethod
    def get_activities(self)->list[ActivityInfo]:
        ...

    @abstractmethod
    def delete_game(self, activity_id:uuid.UUID):
        ...

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






