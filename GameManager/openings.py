from abc import ABC, abstractmethod
import hashlib

import pandas as pd

class OpeningLibrary(ABC):
    """
    Abstract class that idenifies opening
    moves
    """

    def __init__(self) -> None:
        super().__init__()
        self._openings_count:int = 0

    @property
    def openings_count(self)->int:
        """
        Returns:
            int: number of openings
        """
        return self._openings_count

    @abstractmethod
    def get_opening_name(self, moves:list[str])->str|None:
        """
        get the name of an opeing based on series 
        of moves
        """

class OpeningLibraryDF(OpeningLibrary):
    """
    Pandas dataframe implementation of OpeningLibray
    """
    OPENING_COLUMNS:list[str] = ['eco', 'name', 'pgn', 'uci', 'game_hash']

    def __init__(self, openings:pd.DataFrame) -> None:
        """
        Args:
            openings (pd.DataFrame): DataFrame must contain these columns
            'eco', 'name', 'pgn', 'uci', 'game_hash'

        Raises:
            ValueError: if opening DataFrame is not correct
        """
        super().__init__()

        if sorted(OpeningLibraryDF.OPENING_COLUMNS) != sorted(list(openings.columns)):
            raise ValueError("openings parameter does not contain correct columns")

        self._openings_df:pd.DataFrame = openings
        print(self._openings_df['game_hash'].to_list())
        self._openings_count = len(self._openings_df)

    def get_opening_name(self, moves:list[str]):
        hasher = hashlib.sha256()
        for s in moves:
            hasher.update(s.encode('utf-8'))
        test:str = hasher.hexdigest()
        print(test)
        df:pd.DataFrame = self._openings_df[self._openings_df["game_hash"] == test]
        
        return None if df.empty else df.iloc[0]['name']
