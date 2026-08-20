# pylint: disable=redefined-outer-name

from dataclasses import dataclass, field
from typing import Tuple, Any, Optional, override
import math
from enum import Enum

import tkinter as tk
from PIL import ImageTk

from chess import (STARTING_FEN, Square, SquareSet,
                   square,
                   SQUARES,
                   square_rank,
                   square_file,
                   square_name,
                   Piece,
                   Board, PieceType,
                   Move, Outcome)

from Input import EventDispatcher, Event
from . import load_pieces, PIECE_LETTERS

LIGHT_SQUARE:Tuple[int, int, int] = (238, 238, 210)
DARK_SQUARE:Tuple[int, int, int] = (118, 150, 86)
SELECTED_SQUARE:Tuple[int, int, int] = (255, 255, 0)

LIGHT_SQUARE_COLOR = f"#{LIGHT_SQUARE[0]:x}{LIGHT_SQUARE[1]:x}{LIGHT_SQUARE[2]:x}"
DARK_SQUARE_COLOR = f"#{DARK_SQUARE[0]:x}{DARK_SQUARE[1]:x}{DARK_SQUARE[2]:x}"
SELECTED_SQUARE_COLOR:str ="#FFFF00"
MOVE_COLOR:str = "#64B7DA"
CIRCLE_COLOR:str = "#083808"
LEGAL:str = "#785DB7"

LEGAL_TAG:str = "legal_tag"

class MOVE_ID(Enum):
    CAPTURE = 1
    ATTACKING = 2
    ATTACKED = 3

@dataclass
class MoveResult:
    move:Move
    piece_id:Piece
    attacking:list[dict[Square, Optional[Piece]]] = field(default_factory=list)
    attacked_by:list[dict[Square, Optional[Piece]]] = field(default_factory=list)
    captured_piece:Optional[Piece] = None
    gives_check:bool = False
    is_kingside_castling:bool = False
    is_queenside_castling:bool = False
    is_game_over:bool = False
    outcome:Optional[Outcome] = None


class SmartChessBoard(Board, EventDispatcher):
    """Tkinter display for chess game that extends chess.board """

    TKINTER_LEFT_CLICK:str = "<Button-1>"
    def __init__(self, canvas:tk.Canvas, 
                 pieces_map:dict[str, str], 
                 fen: str | None = STARTING_FEN, *,
                 show_pieces:bool = True,
                 chess960: bool = False,
                 show_algebraic:bool=False,
                 show_legal_move:bool = True,
                 show_to_from:bool = True) -> None:        
        
        EventDispatcher.__init__(self)
        self._canvas = canvas
        self._canvas.bind(self.TKINTER_LEFT_CLICK, self._left_mouse_click)
        self._square_size:int = int(canvas.cget("width")) // 8

        self._image_map:dict[str, ImageTk.PhotoImage] = load_pieces(pieces_map,
                                                                    self._square_size)

        self._selected_square:Optional[Square]|None = None        
        self._show_algebraic:bool = show_algebraic
        self._show_pieces: bool = show_pieces

        self._square_to_piece_map:dict[Square, Optional[int]] = {}
        for s in SQUARES:
            self._square_to_piece_map[s] = None
        
        self._initialize()
        super().__init__(None, chess960=chess960)
        if fen is not None:
            self.set_fen(fen)
            self._set_all_pieces_display()

             
    @property
    def show_algebraic(self)->bool:
        """
        show/hide agebric text on board
        """
        return self._show_algebraic
    @show_algebraic.setter
    def show_algebraic(self, show:bool):
        for s in SQUARES:
            sid:int = self._canvas.find_withtag(square_name(s))[0]
            self._canvas.itemconfigure(sid, state=('normal' if show else 'hidden'))
        self._show_algebraic = show
    
    def set_moves_squares(self, move:Move|None)->None:
        """
         Changes background colors of where a move
         originated and ended
         
         Args:
            move (Move): Where the move started, if None, 
            clears all squares

        Returns:
            None
        """
        self._reset_all_backgrounds()

        if move is not None:
            self._canvas.itemconfig(self._get_square_id(move.from_square), fill=MOVE_COLOR)
            self._canvas.itemconfig(self._get_square_id(move.to_square), fill=MOVE_COLOR)

    def clear_board_display(self, clear_pieces:bool=True)->None:
        """
            Clears selected and move squares
            
            Args:
            clear_pieces (bool): is true, clear the pieces

            Returns:
                None
        """
        self.set_selected_square(None)
        self.set_moves_squares(None)

        if clear_pieces:
            self._remove_all_pieces_display()

    def get_selected_square(self)->Square|None:
            """
            Selected is the highlighted square
    
            Returns:
                Square|None: highlighted square
            """
            return self._selected_square

    def set_selected_square(self, sq:Square|None, set_legal:bool=True):
        if self._selected_square is not None:
            self._canvas.itemconfig(self._get_square_id(self._selected_square),
                                    outline="black")
            self._selected_square = None

            if set_legal:
                self._clear_legal_squares()
        if sq is not None:
            self._canvas.itemconfig(self._get_square_id(sq), outline=SELECTED_SQUARE_COLOR)
            self._selected_square = sq

            if set_legal:       
                self._set_legal_square(sq) 

            # TODO:Add attacker and attacked

    def get_legal_squares(self, sq:Square)->list[Square]:
        return [m.to_square for m in self.legal_moves if m.from_square == sq]

    def process_move(self, move:Move)->MoveResult | None:
        print(f"Move: {move.uci()}")
        p:Piece | None = self.piece_at(move.from_square)
        game_over:bool = self.is_game_over()
        if not self.is_legal(move) or p is None:
            return None
        mr:MoveResult = MoveResult(move=move, piece_id=p)
        mr.is_game_over = game_over
        if game_over:
            mr.outcome = self.outcome()
        
        self._clear_display_cues()
        self.push(move)

        if not game_over:
            mr.is_kingside_castling = self.is_kingside_castling(move)
            mr.is_queenside_castling = self.is_queenside_castling(move)
            mr.gives_check = self.gives_check(move)

            if self.is_capture(move):
                mr.captured_piece = self.piece_at(move.to_square)  
            
            atsq:list[int] = [i for i, b in enumerate(self.attacks(move.to_square).tolist()) if b]
            mr.attacking = [{i:self.piece_at(i)} for i in atsq]

            atksq:list[int] = [i for i, b in enumerate(self.attackers(p.color, move.to_square).tolist()) if b]
            mr.attacked_by = [{i:self.piece_at(i)} for i in atksq]
        else:
            mr.outcome = self.outcome()

        return mr

    @override
    def set_piece_at(self, square:Square, piece:Piece|None, promoted:bool=False)->None:
        self._remove_piece_display(square)
        self._set_piece_display(square, piece)

        super().set_piece_at(square, piece, promoted)

    @override
    def remove_piece_at(self, square:Square)->Piece|None:
        self._remove_piece_display(square)
        return super().remove_piece_at(square)

    @override
    def reset(self):
        self._remove_all_pieces_display()
        super().reset()
        self._set_all_pieces_display()

    @override
    def push(self, move: Move) -> None:
        self._remove_piece_display(move.from_square)
        self._set_piece_display(move.to_square, self.piece_at(move.from_square))
        super().push(move)

    @override
    def pop(self)->Move: 
        piece:Optional[Piece] = self.piece_at(self.peek().to_square)
        mv:Move = super().pop()

        self._remove_piece_display(mv.to_square)
        if piece is not None:
            self._set_piece_display(mv.from_square,piece)

        return mv

    @override
    def set_fen(self, fen: str) -> None:
        self.clear_board_display()
        super().set_fen(fen)
        self._set_all_pieces_display()

    def _clear_legal_squares(self):
        self._canvas.delete(LEGAL_TAG)

    def _set_legal_square(self, sq:Square):
        # self._canvas.find_overlapping(x, y, x, y)
        #         canvas.find_closest(x, y)
        ls:list[str] = [square_name(sn) for sn in self.get_legal_squares(sq)]
        print(f"Squares:{sq} = {ls}")
        for square in self.get_legal_squares(sq):
            p:Optional[Piece] = self.piece_at(square)
            if p is None:
                bb:list[float] = self._get_square_bbox(square)
                self._canvas.create_oval(bb[0] + 4, bb[1] + 4, bb[2] -4, bb[3] - 4,
                                    width=0.0, fill=LEGAL, tags=LEGAL_TAG)
            else:
                sym:str = "a" + Piece.symbol(p)
                self._remove_piece_at(square)
                self._set_piece_image(sq, sym)
                
    def _clear_display_cues(self):
        self._clear_legal_squares()
        self.set_selected_square(None)

    def _left_mouse_click(self, event:tk.Event):
        """
        user makes left click

        Args:
            event (tk.Event): event containing x, y coordinates
        """
        file:int = math.floor(event.x / self._square_size)
        rank:int = 7 - math.floor(event.y / self._square_size)
        sq:Square = square(file, rank)
        data:dict[str, Any] = {"square":sq, "selected":sq == self._selected_square}
        self._dispatch(Event.SQUARE_CLICK, data)

    def _reset_all_backgrounds(self)->None:
        for s in SQUARES:
            self._reset_background(s)

    def _reset_background(self, sq:Square)->None:
        """
            resets background to black
            
            Args:
            sq (Square): Square to rest background

            Returns:
                None
        """
        self._canvas.itemconfig(self._get_square_id(sq), fill=self._get_square_color(sq), outline='black')

    def _remove_all_pieces_display(self):
        # for k in self.piece_map():
        #     self._remove_piece_display(k)
        for l in PIECE_LETTERS:
            self._canvas.delete(l)

    def _set_all_pieces_display(self):
        for k, v in self.piece_map().items():
            self._set_piece_display(k, v)

    def _remove_piece_display(self, square:Square):
        pid:Optional[int] = self._square_to_piece_map[square]

        if pid is not None:
            self._square_to_piece_map[square] = None
            self._canvas.delete(pid)

    def _set_piece_display(self, square:Square, piece:Piece|None)->None:
        if piece is not None:
            sym:str = Piece.symbol(piece)
            self._set_piece_image(square, sym )
            
    def _set_piece_image(self, square:Square, name:str):
        img:Optional[ImageTk.PhotoImage] = self._image_map[name]

        if img is not None:
            coords:list[float] = self._get_square_bbox(square)
            pid:int = self._canvas.create_image(coords[0] + 2, coords[1] + 2, tags=name,
                                        anchor=tk.NW, image=img) 
            self._square_to_piece_map[square] = pid

    def _initialize(self):
        """
        Initializes self._board_map_map and creates a background image
                    
        Raises:
            Exception if self._board_map was initialized with 64 values
        """
        self._algebraic_ids = []
        for sq in SQUARES:
            f = square_file(sq)
            r = 7 - square_rank(sq)
            x0:int = f * self._square_size
            y0:int = r * self._square_size
            x1:int = x0 + self._square_size
            y1:int = y0 + self._square_size

            self._canvas.create_rectangle(x0, y0, x1, y1,
                                        tags=f"{square_name(sq)}",
                                        fill=self._get_square_color(sq),
                                        width=3)
            self._canvas.create_text(x0 + 7, y1-7, text=square_name(sq),
                                    tags=f"{square_name(sq)}_an",
                                    fill="red", font=("Arial", 8, "bold"),
                                    state=('normal' if self._show_algebraic else 'hidden'))
            self._square_to_piece_map[sq] = None
    def _get_square_id(self, sq:Square)->int:
        """
            helper to square canvas id
        """
        return self._canvas.find_withtag(square_name(sq))[0]

    def _get_square_bbox(self, square:Square) ->list[float]:
        """
        helper to square coordinates
        """
        return self._canvas.coords(f"{square_name(square)}")

    def _get_square_color(self, sq:Square)->str:
        """
        handy util to get background color
        """
        return LIGHT_SQUARE_COLOR if (square_rank(sq) + square_file(sq)) % 2 == 0 else DARK_SQUARE_COLOR
