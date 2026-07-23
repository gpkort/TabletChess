from typing import Any, Tuple
from pathlib import Path
from dataclasses import fields, asdict
import uuid

import pandas as pd

from .utilites import GamePersister, GameInfo

DEFAULT_PERSIST_DF:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(GameInfo)])

class GamePersisterDF(GamePersister):
    def __init__(self, game_df:pd.DataFrame|None) -> None:
        super().__init__()

        self._game_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(GameInfo)])

        if game_df is not None:
            if list(game_df.columns) != list(self._game_df):
                raise ValueError("Incorrect DataFrame colums!")

            self._game_df = game_df.copy(deep=True)

    @property
    def game_df(self)->pd.DataFrame:
        return self._game_df.copy(deep=True)

    def save_to_disk(self, pickle_path:str):
        self._game_df.to_pickle(pickle_path)

    def save_game(self, game:GameInfo, *, pickle_path:str|None=None):
        game.id = str(uuid.uuid4()) if game.id is None else game.id
        
        df:pd.DataFrame = pd.DataFrame([asdict(game)])
        
        self._game_df = pd.concat([self._game_df, df], ignore_index=True)

        if pickle_path:
            self.save_to_disk(pickle_path=pickle_path)

    def query_games(self, data:dict[str, Any])->Tuple[str, dict[str, GameInfo]]:
        errors:str = ""
        games: dict[str, GameInfo] = {}
        property_names:list[str] = [f.name for f in fields(GameInfo)]

        for prop, val in data.items():
            if prop not in property_names:
                errors += f"{prop} not recognized, "
            else:
                res_df:pd.DataFrame = self._game_df[self._game_df[prop] == val]

                for row in res_df.to_dict('records'):
                    games[row["id"]] = GameInfo(**row)      #type: ignore
                    
        return (("OK" if errors == "" else errors), games)


    def delete_game(self, game:GameInfo):
        uid:str = str(game.id)

        if game.id is not None:
            self._game_df.drop(self._game_df[self._game_df['id'] == uid].index, inplace=True)
        else:
            raise ValueError("Game has no id!")



    # id:UUID
    # FEN:str
    # game_name:str
    # white_player_name:str
    # black_player_name:str
    # game_engine:EngineType|None = None
    # puzzle_id:str|None = None