from typing import Any

from chess import (Board, 
                   Piece, 
                   Square,
                   SQUARES,
                   Move)

from Display.chess_board import SmartChessBoard, ChessBoardInfo
from GameManager import ActivityManager
from Input import Event, EventHandler

class ChessGameManager(ActivityManager):
    def __init__(self, chess_board: SmartChessBoard):
        super().__init__(chess_board)
        self._board:SmartChessBoard = chess_board
        self._board.register_handler(EventHandler(Event.SQUARE_CLICK, self.on_square_click))

    def on_square_click(self, event:Event, data:dict[str, Any]):
        square:Square = data["square"]
        selected:bool = data["selected"]

        if selected:
            self._display_board.clear_board_display(clear_pieces=False)
            return        
        else:
            piece:Piece | None = self._board.piece_at(square)            
            if piece is not None and piece.color != self._board.turn:    
                move:Move = Move
            
                  
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

    