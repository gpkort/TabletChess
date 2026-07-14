from typing import Any

import tkinter as tk
from chess import engine, Square, Board
import chess

from Input import EventHandler, Event, TkButtonInputHandler
from Display import BoardDisplay
from puzzler import Puzzle_Engine


ENGINE:str = r"stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600

class Chessmanager:
    WINDOW_CLOSE:str = "WM_DELETE_WINDOW"

    def __init__(self, display_width:int, display_height, engine_path:str, board_size: int,
                 pieces_map:dict[str, str], 
                 *, 
                 is_single_player:bool = True, 
                 single_player_is_white:bool = True,
                 engine_skill_level:int = 0):
        
        self.root = tk.Tk()
        self.root.title("Chess")
        self.board_display:BoardDisplay = BoardDisplay(self.root, display_width, display_height, board_size, pieces_map)
        self.board_display.register_handler(EventHandler(Event.SQUARE_CLICK, self.handle_square_selection))
        self.root.protocol(self.WINDOW_CLOSE, self.on_closing)

        self.engine:engine.SimpleEngine = engine.SimpleEngine.popen_uci(engine_path)
        self.engine.configure({"Skill Level": engine_skill_level})
        self.limit = engine.Limit(time=0.5)
        self.board:Board = Board()

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

    def on_closing(self):
        """
        Callback from close root frame
        """
        self.engine.close()
        self.root.destroy()

    

    def new_game(self):
        """
        Start a new game   
        """
        self.board.reset()
        self.board_display.update_board_display()  

    def get_legal_squares(self, square:Square)->list[Square]:
        """
            return squares that can be leagally moved to
        Args:
            square (chess.Square): starting square
        """
        return [m.to_square for m in self.board.legal_moves if m.from_square == square]
    
    def handle_square_selection(self, event:Event, data:dict[str, Any]):
        """
        Either select a piece or move a piece if it's your turn and you clicked a 
        legal square

        Args:
            square (chess.Square): square that user clicked on.
        """
                
        if self.board.is_game_over() or self.board.turn != self.player_color:
            return

        if self.selected_square is None:
            piece:chess.Piece | None = self.board.piece_at(square)            
            if piece is None or piece.color != self.board.turn:
                return
            self.legal_squares = self.get_legal_squares(square)
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
        self.update_board_display()


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