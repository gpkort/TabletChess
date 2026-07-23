from typing import Any

import tkinter as tk
import pandas as pd
from chess import (engine, 
                   Square, 
                   Board, 
                   Piece)
import chess

from Input import EventHandler, Event, TkButtonInputHandler
from Display import BoardDisplay, DisplayInfo
from .puzzler import PuzzleEngine
from .game_data import GamePersisterDF, GameInfo

ENGINE:str = r"stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600


class ChessManager:
    WINDOW_CLOSE:str = "WM_DELETE_WINDOW"

    def __init__(self, display_width:int, display_height, board_size: int,
                 engine_path:str,
                 pieces_map:dict[str, str],
                 puzzle_engine:PuzzleEngine,
                 game_data:GamePersisterDF,
                 *, 
                 is_single_player:bool = True, 
                 single_player_is_white:bool = True,
                 engine_skill_level:int = 0):
        
        self.root = tk.Tk()
        self.root.title("Chess")
        self.board_display:BoardDisplay = BoardDisplay(self.root, display_width, display_height, board_size, pieces_map)
        self.board_display.register_handler(EventHandler(Event.SQUARE_CLICK, self.handle_square_selection))
        self.root.protocol(self.WINDOW_CLOSE, self.on_closing)
        self.buttons:TkButtonInputHandler = TkButtonInputHandler(self.root)
        self.buttons.register_handler(EventHandler(Event.NEW, self.button_handler))
        self.buttons.register_handler(EventHandler(Event.PUZZLES, self.button_handler))

        self.engine:engine.SimpleEngine = engine.SimpleEngine.popen_uci(engine_path)
        self._engine_file = engine_path
        self.engine.configure({"Skill Level": engine_skill_level})
        self.limit = engine.Limit(time=0.5)
        self.board:Board = Board()

        self.puzzle_engine:PuzzleEngine = puzzle_engine
        self.game_data:GamePersisterDF = game_data
        
        self.is_single_player:bool = is_single_player
        self.player_color:chess.Color = chess.WHITE if single_player_is_white else chess.BLACK
        self.selected_square:chess.Square|None = None
        self.previous_square:chess.Square|None = None
        self.target_square:chess.Square|None = None
        self.legal_squares:list[chess.Square] = []
        
        
    def __del__(self):
        try:
            self.engine.quit()
            self.board_display.unregister_all_handlers()
        except engine.EngineTerminatedError as e:
            print(e)

    def start(self):
        self.root.mainloop()

    def on_closing(self):
        """
        Callback from close root frame
        """
        self.engine.close()
        self.root.destroy()

    def button_handler(self, event:Event, data:dict[str, Any]):
        """
        Handles button events
        """ 
        if event == Event.NEW:
            if len(self.board.move_stack) > 0:
                self.save_current_game()
                
            self.board_display.update_board_display(self.reset_game())
        if event == Event.PUZZLES:       
            self.handle_puzzle()
    
    def handle_square_selection(self, event:Event, data:dict[str, Any]):
        """
        Either select a piece or move a piece if it's your turn and you clicked a 
        legal square

        Args:
            square (chess.Square): square that user clicked on.
        """
                
        if self.board.is_game_over() or self.board.turn != self.player_color:
            return
        
        square:Square = data["square"]

        if self.selected_square is None:
            piece:chess.Piece | None = self.board.piece_at(square)            
            if piece is None or piece.color != self.board.turn:
                return
            self.legal_squares = [m.to_square for m in self.board.legal_moves if m.from_square == square]
            self.selected_square = square
            self.previous_square = None
            self.target_square = None
        else:
            if self.selected_square == square:
                self.selected_square = None
                self.previous_square = None
                self.target_square = None
            else:
                piece:chess.Piece | None = self.board.piece_at(self.selected_square)
                if piece is None or piece.color != self.board.turn:
                    return
                if square in self.legal_squares:
                    self.board.push(chess.Move(self.selected_square, square))
                    pr:engine.PlayResult = self.engine.play(self.board, self.limit)
                    if pr.move:
                        self.board.push(pr.move)
                        self.previous_square = pr.move.from_square
                        self.target_square = pr.move.to_square
                    self.selected_square = None
                    self.legal_squares.clear()
        
        
        self.board_display.update_board_display(DisplayInfo(
            self.selected_square,
            self.previous_square,
            self.target_square,
            self.legal_squares,
            self.get_piece_location()
        ))

    def handle_puzzle(self):
        ...

    def reset_game(self)->DisplayInfo:
        self.board.reset()
        self.selected_square = None
        self.previous_square = None
        self.target_square = None
        self.legal_squares = []
        return DisplayInfo(
                        self.selected_square,
                        self.previous_square,
                        self.target_square,
                        self.legal_squares,
                        self.get_piece_location()
                        )
    
    def get_piece_location(self)->dict[chess.Square, str]:
        piece_location:dict[chess.Square, str] = {}
        for i in range(64):
            piece:Piece|None = self.board.piece_at(i)

            if piece:
                piece_location[i] = piece.symbol()
        return piece_location

    def save_current_game(self, puzzle_id:str|None=None):
        if self.board_display.get_player_yes_no("Save Game", "Do you want to save?"):
            name:str|None = self.board_display.get_player_input("", "Name of game:")
            if name is None or len(name) == 0:
                self.board_display.set_palyer_alert("Status", "Save Canceled.")
            else:
                game:GameInfo = GameInfo(FEN=self.board.fen(), 
                                         game_name=name, 
                                         white_player_name="white", 
                                         black_player_name="black",
                                         game_engine_file=self._engine_file,
                                         puzzle_id=puzzle_id
                                         )
                self.game_data.save_game(game)

                print(self.game_data.game_df.head())

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