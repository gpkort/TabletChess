from typing import Any, Tuple
from pathlib import Path
from dataclasses import fields, asdict
import uuid

import pandas as pd

from .utilites import ActivityPersister, ActivityInfo, SaveOption, ActivityPersisterSaveException

class ActivityPersisterDF(ActivityPersister):
    def __init__(self, activity_df:pd.DataFrame|None, *, max_activites_save:int=15) -> None:
        super().__init__(max_activity_save=max_activites_save)

        self._activity_df:pd.DataFrame = pd.DataFrame(data=None,columns=[f.name for f in fields(ActivityInfo)])

        if activity_df is not None:
            if list(activity_df.columns) != list(self._activity_df.columns):
                raise ValueError("Incorrect DataFrame colums!")

            self._game_df = activity_df.copy(deep=True)

        self._activity_count = len(self._game_df)

    @property
    def game_df(self)->pd.DataFrame:
        return self._game_df.copy(deep=True)
    
    def save_to_disk(self, pickle_path:str):
        self._game_df.to_pickle(pickle_path)

    def save_activity(self, activity:ActivityInfo, save_option:SaveOption=SaveOption.NO_OVERWITE):
        """
        Save activity to data frmae. Note, does not save to disk
        """
        has_room:bool = self._activity_count < self._max_activity_save
        if has_room and not (save_option == SaveOption.OVERWRITE_FIRST or save_option == SaveOption.OVERWRITE_LAST):
            mess:str = f"Activity storage is full: current activity count: {self._activity_count}, max is {self._max_activity_save}"
            raise ActivityPersisterSaveException(mess)

        if activity.activity_id is None:
            activity.activity_id = uuid.uuid4()

        df:pd.DataFrame = pd.DataFrame([asdict(activity)])
        concat_order:list[pd.DataFrame] = [df, self._game_df]
        drop_index:int = -1

        if save_option == SaveOption.OVERWRITE_LAST:
            concat_order.reverse()
            drop_index = -1

        if not has_room:
            self._game_df.drop(self._game_df.index[drop_index], inplace=True)
        
        self._game_df = pd.concat(concat_order, ignore_index=True)
        self._activity_count = len(self._game_df)
    
    def get_activities(self)->list[ActivityInfo]:
        return [ActivityInfo(**act) for act in self._activity_df.to_dict('records')]     #type: ignore
    
    def delete_game(self, activity_id:uuid.UUID):
        drop_index:pd.Index[Any] = self._game_df[self._game_df['activity_id'] == activity_id].index
        if len(drop_index) == 0:
            raise ValueError(f"Activity with {str(activity_id)} not found!")

        self._game_df.drop(drop_index, inplace=True)
