from typing import Any, Optional
from dataclasses import dataclass
import uuid
from datetime import datetime
import json

from chess import (Piece, 
                   Square,
                   Move,
                   engine,
                   Color,
                   WHITE,
                   BLACK,
                   STARTING_FEN,
                   square_name,)


from Display import SmartChessBoard
from GameManager import ActivityManager
from Input import Event, EventHandler


class GameConfiguration:
    # class to hold data about specific, 
    # if the game was against ches
    def __init__(self,
                 id:Optional[uuid.UUID]=None,
                 name:Optional[str]=None,
                 fen:str=STARTING_FEN,
                 move_stack:list[Move] = [],
                 player_1_color:Color = WHITE,
                 player_1_name:str="Player 1",
                 player_2_name:str="Player 2",
                 engine_path:Optional[str]=None,
                 engine_elo:int=1100):


        self.id:uuid.UUID = id or uuid.uuid4()
        self.name:str = name or datetime.now().strftime("game_%Y%m%d_%H%M%S")
        self.fen:str = fen 
        self.move_stack = move_stack
        self.player_1_color:Color = player_1_color
        self.player_2_color:Color = BLACK if player_1_color == WHITE else WHITE
        self.player_1_name:str = player_1_name
        self.player_2_name:str = player_2_name if engine_path is None else "Engine"
        self.engine_path:str | None = engine_path
        self.engine_elo:int = engine_elo

    def toJson(self, pretty_print=False)->str:

        return json.dumps({
                        "id": f"{str(self.id)}",
                        "name": f"{self.name}",
                        "fen": f"{self.fen}",
                        "move_stack":", ".join([m.uci() for m in self.move_stack]),
                        "player_1_color": f"{self.player_1_color}",
                        "player_2_color": f"{self.player_2_color}",
                        "player_1_name": f"{self.player_1_name}",
                        "player_2_name": f"{self.player_2_name}",
                        "engine_path": f"{self.engine_path}",
                        "engine_elo": self.engine_elo
                        }, indent=pretty_print)

    @staticmethod
    def fromJson(json_str:str)->"GameConfiguration":
        data:dict[str, Any] = json.loads(json_str)

        p_color:Color = WHITE if str(data.get("player_1_color", "WHITE")).upper() == "WHITE" else BLACK

        return GameConfiguration(id = data.get("id"),
                                name = data.get("name"),
                                fen = data.get("fen") or STARTING_FEN,
                                move_stack= [Move.from_uci(m) for m in data.get("move_stack", [])],
                                player_1_color= p_color,
                                player_1_name= data.get("player1_name",  "Player 1"),
                                player_2_name= data.get("player2_name", "Player 2"),
                                engine_path = data.get("engine_path"),
                                engine_elo = data.get("engine_elo", 1100)
        )

class ChessGameManager(ActivityManager):
    def __init__(self, chess_board: SmartChessBoard, chess_engine:engine.SimpleEngine ):
        super().__init__(chess_board)
        self._board:SmartChessBoard = chess_board
        self._board.register_handler(EventHandler(Event.SQUARE_CLICK, self.on_square_click))
        self._board.register_handler(EventHandler(Event.DOUBLE_CLICK, self.on_square_double_click))

        self._engine:engine.SimpleEngine = chess_engine
        self.game_config:GameConfiguration | None = None

    def on_square_click(self, event:Event, data:dict[str, Any])->None:
        square:Square = data["square"]
        selected_sq:Square | None = data["selected_square"]
        
        if selected_sq == square:
            self._display_board.clear_display_cues()
            return        
        else:
            piece:Piece | None = self._board.piece_at(square) 

            if piece is not None and piece.color != self._board.turn:
                return

            if piece is not None and piece.color == self._board.turn:
                if selected_sq is not None:
                    self._display_board.clear_display_cues()
                self._board.set_selected_square(square)
            else:
                self.make_move(Move(selected_sq, square))     #type:  ignore

    def on_square_double_click(self, event:Event, data:dict[str, Any])->None:
        print(f"Square: {square_name(data["square"])}")

    def make_move(self, move:Move):   
        if self._board.process_move(move):
            print(str(self._board.get_board_status()))
        else:
            print("Illegal")

    def load_game(self, config:GameConfiguration):
        self.game_config = config
        self._board.set_fen(self.game_config.fen)

    