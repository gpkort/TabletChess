from typing import Any, Tuple
from enum import Enum
from time import sleep

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
            self.handle_new_request(event)
            
        if event == Event.NEW_PUZZLE:       
            self.handle_new_request(event)
    
    def handle_square_selection(self, _:Event, data:dict[str, Any]):
        """
        Either select a piece or move a piece if it's your turn and you clicked a 
        legal square

        Args:
            square (chess.Square): square that user clicked on.
        """
                
        if self._board.is_game_over() or self._board.turn != self._player_color:
            return
        
        square:Square = data["square"]

        if self._selected_square == square:
            self._selected_square = None
            self._previous_square = None
            self._target_square = None
            self._legal_squares = []

            self._update_display_current()
            return

        if self._selected_square is None:
            piece:chess.Piece | None = self._board.piece_at(square)            
            if piece is None or piece.color != self._board.turn:
                return
            self._legal_squares = [m.to_square for m in self._board.legal_moves if m.from_square == square]
            self._selected_square = square

            self._update_display_current()
            return        
        else:
            if square in self._legal_squares:
                self._board.push(chess.Move(self._selected_square, square))                
                self._selected_square = None
                self._previous_square = None
                self._target_square = None
                self._legal_squares.clear()

                if self._manager_state == ManagerState.GAME_STARTED:
                    self.game_move_response()
                elif self._manager_state == ManagerState.PUZZLE_STARTED:
                    self.puzzle_move_response()

    def handle_new_request(self, event:Event):
        if len(self._board.move_stack) > 0:
            res:SaveResult = self.save_current_activity()

            if res != SaveResult.CANCEL:
                return
            
        if event == Event.NEW_GAME:            
            self.launch_new_game()
        elif event == Event.NEW_PUZZLE:
            self.launch_new_puzzle()            

    def launch_new_game(self):
        self._board = Board()
        self._board_display.update_board_display(self.reset_game())
        self._current_activity = ActivityInfo(FEN=self._board.fen(), activity_name="New_Game")
        self._manager_state = ManagerState.GAME_STARTED

    def launch_new_puzzle(self):
        self._current_activity = self._puzzle_engine.get_random_puzzle()
        self._board = Board(self._current_activity.FEN)
        try:
            mv:chess.Move = chess.Move.from_uci(self._current_activity.puzzle_moves[0])
            if self._board.is_legal(mv):
                self._board.push(mv)
            else:
                # TODO: handle error
                ...
        except chess.InvalidMoveError as e:
            # TODO: handle error
            ...

        self._player_color = self._board.turn
        self._board_display.update_board_display(self.reset_game())
        self._manager_state = ManagerState.PUZZLE_STARTED
        game_txt:str = f"Puzzle: {self._current_activity.activity_name}, Themes: {", ".join(self._current_activity.puzzle_themes)}\n"

        game_txt += f"Total Moves: {len(self._current_activity.puzzle_moves) / 2}"
        if self._current_activity.puzzle_rating is not None:
            game_txt += f" Ratings: {self._current_activity.puzzle_rating}\n"
        game_txt += f"{self._current_activity.puzzle_moves}\n"
        game_txt += f"{'White' if self._board.turn == chess.WHITE else "Black"} to move."
        self._board_display.set_text(game_txt)

    def game_move_response(self):
        if not self.check_status():
            #do sumpin bigly
            return

        # print(self._engine.analyse(self._board, engine.Limit(time=0.5)))
        pr:engine.PlayResult = self._engine.play(self._board, self._limit)
        # print(f"Play Result = {pr}")
        # sleep(2)
        if pr.move is not None:
            self.move_opponent(pr.move)

        if not self.check_status():
            ...
            #do sumpin bigly
        self._update_display_current()     

    def puzzle_move_response(self):
        try:
            last_mv:chess.Move = self._board.peek()
            mess:str = ""
            
            if last_mv.uci() != self._current_activity.puzzle_moves[len(self._board.move_stack) - 1]:        #type: ignore
                self.take_back_move()
                piece:chess.Piece | None = self._board.piece_at(last_mv.from_square)
                if piece is not None:
                    mess = f"{chess.piece_name(piece.piece_type)} to {chess.square_name(last_mv.to_square)} is not correct"
            else:
                if len(self._board.move_stack) == len(self._current_activity.puzzle_moves):     #type: ignore
                    mess = "Great Work, you solved it!"
                    #do sumpin bigly
                else:
                    mess = "Correct, keep going!"
                    print(self._current_activity.puzzle_moves[len(self._board.move_stack)]) #type: ignore
                    self.move_opponent(chess.Move.from_uci(self._current_activity.puzzle_moves[len(self._board.move_stack)]))  #type: ignore
            self._board_display.append_text(mess)
            self._update_display_current()
        except IndexError as ie:
            self._board_display.append_text(f"ERROR: {ie}")

    def move_opponent(self, move:chess.Move):
        
        if self._board.is_legal(move):
            self._board.push(move)
            self._previous_square = move.from_square
            self._target_square = move.to_square


    def take_back_move(self)->chess.Move:
        mv:chess.Move = self._board.pop()
        self._board_display.update_board_display(self.reset_game())
        return mv

    def check_status(self)->bool:
        still_going:bool = True
        oc:chess.Outcome | None = self._board.outcome(claim_draw=True)
        if oc is not None:
            out:str = "GAME OVER:\n"
            if oc.winner is not None:
                out += f"{'BLACK' if oc.winner == chess.BLACK else 'WHITE'} won."
            else:
                out += "The game was a draw!"
            self._board_display.set_text(out)
            still_going = False

        return still_going

    def reset_game(self)->DisplayInfo:       
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

    def _update_display_current(self):
        self._board_display.update_board_display(DisplayInfo(
            self._selected_square,
            self._previous_square,
            self._target_square,
            self._legal_squares,
            self.get_piece_location()
        ))
    
    def get_piece_location(self)->dict[chess.Square, str]:
        piece_location:dict[chess.Square, str] = {}
        for i in range(64):
            piece:Piece|None = self._board.piece_at(i)

            if piece:
                piece_location[i] = piece.symbol()
        return piece_location

    def save_current_activity(self)->SaveResult:
        res , name = self._board_display.save_activity_prompt()
        
        if res == SaveResult.SAVE:
             if self._current_activity is not None:
                self._current_activity.activity_name = name
                self._current_activity.activity_moves = [m.uci() for m in self._board.move_stack]
                self._current_activity.game_engine_file = self._engine_file
                self._current_activity.activity_outcome = self._board.outcome()
                self._game_data.save_activity(self._current_activity, SaveOption.OVERWRITE_FIRST)

        return res
                

        # if self._board_display.get_player_yes_no("Save Activity", "Do you want to save?"):
        #     name:str|None = self._board_display.get_player_input("", "Name of game:")
        #     if name is None or len(name) == 0:
        #         self._board_display.set_player_alert("Status", "Save Canceled.")
        #     else:
        #         if self._current_activity is not None:
        #             self._game_data.save_activity(self._current_activity, SaveOption.OVERWRITE_FIRST)
        #             return True


        return False
