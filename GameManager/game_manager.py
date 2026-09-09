# pylint: disable=missing-module-docstring
from typing import Any, Optional, Tuple
import uuid
from datetime import datetime
import json

import tkinter as tk

from chess import (Piece, 
                   Square,
                   Move,
                   engine,
                   Color,
                   WHITE,
                   BLACK,
                   STARTING_FEN,
                   square_name,
                   piece_name                  
                   )

from Display import SmartChessBoard
from GameManager import ActivityManager
from Input import Event, EventHandler, ChessUI
from .coach import ChessCoach


class GameConfiguration:
    """
    Information representing a Chess game
    """
    def __init__(self,
                 game_id:Optional[uuid.UUID]=None,
                 name:Optional[str]=None,
                 fen:str=STARTING_FEN,
                 move_stack:list[Move] = list(),
                 player_1_color:Color = WHITE,
                 player_1_name:str="Player 1",
                 player_2_name:str="Player 2",
                 engine_path:Optional[str]=None,
                 engine_elo:int=1100):


        self.game_id:uuid.UUID = game_id or uuid.uuid4()
        self.name:str = name or datetime.now().strftime("game_%Y%m%d_%H%M%S")
        self.fen:str = fen 
        self.move_stack = move_stack
        self.player_1_color:Color = player_1_color
        self.player_2_color:Color = BLACK if player_1_color == WHITE else WHITE
        self.player_1_name:str = player_1_name
        self.player_2_name:str = player_2_name if engine_path is None else "Engine"
        self.engine_path:str | None = engine_path
        self.engine_elo:int = engine_elo

    def toJson(self, pretty_print=False)->str:      # pylint: disable=invalid-name
        """
        Json representation of instance of Game Configuration

        Args:
            pretty_print (bool, optional): indents json. Defaults to False.

        Returns:
            str: Json representation of instance of Game Configuration
        """
        return json.dumps({
                        "game_id": f"{str(self.game_id)}",
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
    def fromJson(json_str:str)->"GameConfiguration":    # pylint: disable=invalid-name
        """
        Create an instance of GameConfiguration from
        properly formed JSON

        Args:
            json_str (str): Properly formed JSON representation
            of GameConfiguration

        Returns:
            GameConfiguration: GameConfiguration Instantce
        """
        data:dict[str, Any] = json.loads(json_str)
        is_white:bool = str(data.get("player_1_color", "WHITE")).upper() == "WHITE"
        p_color:Color = WHITE if is_white else BLACK

        return GameConfiguration(game_id = data.get("game_id"),
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
    """
    Chess Game Manager
    """
    def __init__(self,
                 chess_board: SmartChessBoard,
                 chess_ui:ChessUI,
                 chess_engine:engine.SimpleEngine, *,
                 fen:str = "",
                 single_player:bool=True, 
                 coaching:bool=True ):

        super().__init__(chess_board)
        self.single_player:bool=single_player
        self._coaching:bool = coaching        

        self._board:SmartChessBoard = chess_board
        self._board.register_handler(EventHandler(Event.SQUARE_CLICK, self._on_square_click))
        self._board.register_handler(EventHandler(Event.DOUBLE_CLICK, self._on_square_double_click))
        if fen != "":
            self._board.set_board_fen(fen)

        self._engine:engine.SimpleEngine = chess_engine
        self.game_config:GameConfiguration | None = GameConfiguration(player_1_name="Greg")
        self.is_playing:bool = False
        self._pending_square:Square|None = None
        
        self._chess_ui:ChessUI = chess_ui
        self._widgets:list[tk.Widget] = []
        self._initialize_frame()

#region events
    def _on_square_click(self, _:Event, data:dict[str, Any])->None:
        square:Square = data["square"]
        selected_sq:Square | None = data["selected_square"]
        piece:Piece | None = self._board.piece_at(square)

        if selected_sq == square:
            self._display_board.clear_display_cues()
            return

        if piece is None:
            self._display_board.clear_display_cues()
            if selected_sq is not None:
                self._make_move(Move(selected_sq, square)) 
        else:
            if selected_sq is not None:
                if  piece.color == self._board.turn:
                    self._display_board.clear_display_cues()
                    self._board.set_selected_square(square)
                else:
                    self._make_move(Move(selected_sq, square))
            else:
                if  piece.color == self._board.turn:
                    self._display_board.clear_display_cues()
                    self._board.set_selected_square(square)
                else:
                    self._display_board.clear_display_cues()

    def _on_square_double_click(self, _:Event, data:dict[str, Any])->None:        
        print(f"Square: {square_name(data["square"])}")
        
    def on_square_click(self, event:Event, data:dict[str, Any]):
            pass
#endregion

    def _make_move(self, move:Move):
        if self._coaching:
            if self._pending_square is None:
                self._pending_square = move.to_square
                print(self._analyze(move))
                return
            else:
                self._pending_square = None

        if self._board.process_move(move):
            info:engine.InfoDict = self._engine.analyse(self._board.chess_board,
                                                    engine.Limit(time=0.1))
            # {'string': 'Network replica 1: Shared memory.', 'depth': 14, 'seldepth': 22, 
            #  'multipv': 1, 'score': PovScore(Cp(-43), BLACK), 'nodes': 77664, 'nps': 776640, 
            #  'hashfull': 26, 'tbhits': 0, 'time': 0.1, 
            #  'pv': [Move.from_uci('e7e5'), Move.from_uci('g1f3')], 'upperbound': True}
            if self.single_player:
                pr:engine.PlayResult = self._engine.play(board=self._board.chess_board,
                                                         limit=engine.Limit(time=0.5))
                if pr.move is not None:
                    self._board.process_move(pr.move)
                    # self._chess_ui.append_text()

    def _load_game(self, config:GameConfiguration):
        self.game_config = config
        self._board.set_fen(self.game_config.fen)

        # rnbqk1nr/pppp1ppp/8/4p1Q1/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 2

    def _initialize_frame(self)->None:
        self._widgets = []
        ng:tk.Widget = tk.Button(self._chess_ui.widget_frame, text="New Game",
                                command=lambda: self._load_game(GameConfiguration.fromJson("{}")))
        ng.grid(row=1, column=1)
        self._widgets.append(ng)

    def _analyze(self, move:Move)->str:
        piece:Piece | None = self._board.piece_at(move.to_square)
        if piece is None:
            return f"Could not Analyze move: {move.uci()}"

        p_name:str = piece_name(piece.piece_type)
        protect_list:list[Tuple[Piece, Square]] | None = self._board.get_protectors(move.to_square)
        attack_list:list[Tuple[Piece, Square]] | None = self._board.get_attackers(move.to_square)
        protectors:list[Tuple[str, str]] = []
        attackers:list[Tuple[str, str]] = []
        mate_in:list[list[Move]] = ChessCoach.mate_in_n(self._board.chess_board, self._board.turn)

        if protect_list is not None:
            protectors:list[Tuple[str, str]] = [(p.symbol(), square_name(s)) for p, s in protect_list]

        if attack_list is not None:
            attackers:list[Tuple[str, str]] = [(p.symbol(), square_name(s)) for p, s in attack_list]

        result:str = f"Move: {move.uci()}\n"
        result += f"Piece {p_name} at {square_name(move.to_square)}"
        result += f"Protected By: {protectors} \n"
        result += f"Attacked By: {attackers} \n"

        if len(mate_in) > 0:
            c:str = "White" if self._board.turn else "Black"
            result += f"{c} can mate in {min([len(arr) for arr in mate_in])} moves!/n"


        return result

    def _pin_to_k_string(self, piece:Piece, square:Square)->str:
        ks:Square | None = self._board.king(self._board.turn)

        if ks is not None and self._board.is_pinned(self._board.turn, square):
            pn:str = piece_name(piece.piece_type)
            sn:str = square_name(square)
            kstr:str = square_name(ks)
            return f"{pn} at {sn} is pinned to the king at {kstr}.\n"

        return ""


   

    