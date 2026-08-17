from typing import Any

from chess import (Board, 
                   Piece, 
                   Square,
                   SQUARES,
                   Move)

from Display import SmartChessBoard
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
            ss:Square | None = self._board.get_selected_square()
            piece:Piece | None = self._board.piece_at(square) 

            if piece is not None and piece.color == self._board.turn: 
                if ss is None:
                    return
                else:
                    self.make_move(Move(ss, square))     #type:  ignore

    def make_move(self, move:Move):
        if move in self._board.legal_moves:
            self._board.push(move)
                  
        # else:
        #     if square in self._legal_squares:
        #         self._board.push(chess.Move(self._selected_square, square))                
        #         self._selected_square = None
        #         self._previous_square = None
        #         self._target_square = None
        #         self._legal_squares.clear()

        #         if self._manager_state == ManagerState.GAME_STARTED:
        #             self.game_move_response()
        #         elif self._manager_state == ManagerState.PUZZLE_STARTED:
        #             self.puzzle_move_response()

    def new_game(self):
        self._display_board.reset()

    