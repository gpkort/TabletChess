from typing import Any, Tuple
from enum import Enum

import tkinter as tk
import pandas as pd
from chess import (engine, 
                   Square, 
                   Board, 
                   Piece)
import chess

from Input import EventHandler, Event, TkButtonInputHandler
from Display import BoardDisplay, DisplayInfo, SaveResult
from .puzzler import PuzzleEngine
from .game_data import ActivityPersisterDF, SaveOption, ActivityPersisterSaveException
from .utilites import ActivityInfo

ENGINE:str = r"stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600

class ManagerState(Enum):
    IDLE = 0
    GAME_STARTED = 1
    PUZZLE_STARTED = 2
    GAME_REVIEW_STARTED = 3


class ChessManager:
    WINDOW_CLOSE:str = "WM_DELETE_WINDOW"

    def __init__(self, display_width:int, display_height, board_size: int,
                 engine_path:str,
                 pieces_map:dict[str, str],
                 puzzle_engine:PuzzleEngine,
                 game_data:ActivityPersisterDF,
                 *,
                 is_single_player:bool = True,
                 single_player_is_white:bool = True,
                 engine_skill_level:int = 0):
        
        self._root = tk.Tk()
        self._root.title("Chess")
        self._board_display:BoardDisplay = BoardDisplay(self._root, display_width, display_height, board_size, pieces_map)
        self._board_display.register_handler(EventHandler(Event.SQUARE_CLICK, self.handle_square_selection))
        self._root.protocol(self.WINDOW_CLOSE, self.on_closing)

        self._game_data:ActivityPersisterDF = game_data
        self._buttons:TkButtonInputHandler = TkButtonInputHandler(self._root)
        self._buttons.register_all_events(self, self.button_handler)

        self._engine:engine.SimpleEngine = engine.SimpleEngine.popen_uci(engine_path)
        self._engine_file = engine_path
        self._engine.configure({"Skill Level": engine_skill_level})
        self._limit = engine.Limit(time=0.5)
        self._board:Board = Board()
        self._puzzle_engine:PuzzleEngine = puzzle_engine
                
        self._is_single_player:bool = is_single_player
        self._player_color:chess.Color = chess.WHITE if single_player_is_white else chess.BLACK
        self._selected_square:chess.Square|None = None
        self._previous_square:chess.Square|None = None
        self._target_square:chess.Square|None = None
        self._legal_squares:list[chess.Square] = []

        self._manager_state:ManagerState = ManagerState.IDLE
        self._current_activity:ActivityInfo|None = None 
        
    def __del__(self):
        try:
            self._engine.quit()
            self._board_display.unregister_all_handlers()
        except engine.EngineTerminatedError as e:
            print(e)

    def start(self):
        self._root.mainloop()

    def on_closing(self):
        """
        Callback from close root frame
        """
        self._engine.close()
        self._root.destroy()

    def button_handler(self, event:Event, data:dict[str, Any]):
        """
        Handles button events
        """ 
        if event == Event.NEW_GAME:
            self.handle_new_game()
            
        if event == Event.NEW_PUZZLE:       
            self.handle_puzzle()
    
    def handle_square_selection(self, event:Event, data:dict[str, Any]):
        """
        Either select a piece or move a piece if it's your turn and you clicked a 
        legal square

        Args:
            square (chess.Square): square that user clicked on.
        """
                
        if self._board.is_game_over() or self._board.turn != self._player_color:
            return
        
        square:Square = data["square"]



        if self._selected_square is None:
            piece:chess.Piece | None = self._board.piece_at(square)            
            if piece is None or piece.color != self._board.turn:
                return
            self._legal_squares = [m.to_square for m in self._board.legal_moves if m.from_square == square]
            self._selected_square = square
            self._previous_square = None
            self._target_square = None
        else:
            if self._selected_square == square:
                self._selected_square = None
                self._previous_square = None
                self._target_square = None
            else:
                piece:chess.Piece | None = self._board.piece_at(self._selected_square)
                if piece is None or piece.color != self._board.turn:
                    return
                if square in self._legal_squares:
                    self._board.push(chess.Move(self._selected_square, square))
                    pr:engine.PlayResult = self._engine.play(self._board, self._limit)
                    if pr.move:
                        self._board.push(pr.move)
                        self._previous_square = pr.move.from_square
                        self._target_square = pr.move.to_square
                    self._selected_square = None
                    self._legal_squares.clear()
        
        
        self._board_display.update_board_display(DisplayInfo(
            self._selected_square,
            self._previous_square,
            self._target_square,
            self._legal_squares,
            self.get_piece_location()
        ))

    def handle_new_game(self):
        if self._manager_state == ManagerState.IDLE:
            self._board_display.update_board_display(self.reset_game())
            self._manager_state = ManagerState.GAME_STARTED
        else:
            if len(self._board.move_stack) > 0:
                self.save_current_activity()                
    
    def handle_puzzle(self):
        puzzle:ActivityInfo = self._puzzle_engine.get_random_puzzle()
        self._current_activity = puzzle
        self._board = Board(puzzle.FEN)
        self._manager_state = ManagerState.PUZZLE_STARTED
        self._player_color = self._board.turn
        self._board_display.update_board_display(self.reset_game(reset_board=False))
        game_txt:str = f"Puzzle: {puzzle.activity_name}, Themes: {puzzle.puzzle_themes}\n"
        game_txt += f"{'White' if self._board.turn == chess.WHITE else "Black"} to move."
        self._board_display.set_text(game_txt)

    def reset_game(self, reset_board:bool=True)->DisplayInfo:
        if reset_board:
            self._board.reset()

        self._selected_square = None
        self._previous_square = None
        self._target_square = None
        self._legal_squares = []
        return DisplayInfo(
                        self._selected_square,
                        self._previous_square,
                        self._target_square,
                        self._legal_squares,
                        self.get_piece_location()
                        )
    
    def get_piece_location(self)->dict[chess.Square, str]:
        piece_location:dict[chess.Square, str] = {}
        for i in range(64):
            piece:Piece|None = self._board.piece_at(i)

            if piece:
                piece_location[i] = piece.symbol()
        return piece_location

    def save_current_activity(self)->bool:
        res:Tuple[SaveResult, str] = self._board_display.save_activity_prompt()
        print(f"SAVE RESULT: {res}")
        # if self._board_display.get_player_yes_no("Save Activity", "Do you want to save?"):
        #     name:str|None = self._board_display.get_player_input("", "Name of game:")
        #     if name is None or len(name) == 0:
        #         self._board_display.set_player_alert("Status", "Save Canceled.")
        #     else:
        #         if self._current_activity is not None:
        #             self._game_data.save_activity(self._current_activity, SaveOption.OVERWRITE_FIRST)
        #             return True


        return False

# root = tk.Tk()
# root.title("Chess")
# board_display:BoardDisplay = BoardDisplay(root, SCREEN_WIDTH, SCREEN_HEIGHT, 480, IMAGE_MAP, 
#                                           engine.SimpleEngine.popen_uci(ENGINE))
# buttons:TkButtonInputHandler = TkButtonInputHandler(root)

# def new_game(_event:Event, _data:dict[str, Any]):
#     board_display.new_game()

# def main():
#     buttons.register_handler(EventHandler(Event.NEW, new_game))

#     root.mainloop()