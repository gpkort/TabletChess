from typing import Any

from chess import (Board, 
                   Piece, 
                   Square,
                   SQUARES)

from Display.chess_board import ChessBoard, ChessBoardInfo, SquareState
from GameManager import ActivityManager
from Input import Event, EventHandler

class ChessGameManager(ActivityManager):
    def __init__(self, chess_board: ChessBoard):
        super().__init__(chess_board)
        self._game_board:Board = Board()

        self._display_board.register_handler(EventHandler(Event.SQUARE_CLICK, self.on_square_click))


    def on_square_click(self, event:Event, data:dict[str, Any]):
        print(data)
        square:Square = data["square"]
        square_state:SquareState = data["state"]

        if square_state.selected:
            self._legal_squares = []
            self._display_board.clear_board_display(clear_pieces=False)
            return        
        else:
            piece:Piece | None = self._board.piece_at(square)            
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

    def new_game(self):
        self._board = Board()
        self._display_board.update_board_display(ChessBoardInfo(piece_location=self.get_piece_location()))

    def get_piece_location(self)->dict[Square, str]:
            piece_location:dict[Square, str] = {}
            for i in SQUARES:
                piece:Piece|None = self._board.piece_at(i)
    
                if piece:
                    piece_location[i] = piece.symbol()
            return piece_location