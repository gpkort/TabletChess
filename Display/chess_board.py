# pylint: disable=redefined-outer-name

from dataclasses import dataclass, field
from typing import Tuple, Any, Optional, override, Literal
import math
from enum import Enum

import tkinter as tk
from PIL import ImageTk

from chess import (STARTING_FEN, Square, 
                   square,
                   SQUARES,
                   square_rank,
                   square_file, KING,
                   square_name, BLACK,
                   Piece, WHITE,
                   Board, Color,
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
class Attack:
    from_sq:Square
    to_sq:Square
    from_piece:Piece
    to_piece:Piece

    def __str__(self) -> str:
        return f"from: {square_name(self.from_sq)} : {self.from_piece.symbol()}, to: {square_name(self.to_sq)} : {self.to_piece.symbol()}, "

@dataclass
class BoardStatus:
    last_move:Move
    turn:Color
    last_piece:Optional[Piece] = None    
    captured_piece:Optional[Piece] = None
    selected_square:Square|None = None
    is_game_over:bool = False
    outcome:Optional[Outcome] = None
    checkers:list[Attack] = field(default_factory=list)
    attacked_by_black:list[Attack] = field(default_factory=list)
    attacked_by_white:list[Attack] = field(default_factory=list)

    def __str__(self) -> str:
        ret:str = f"last_move: {self.last_move.uci()}, turn: {"WHITE" if self.turn else "BLACK"} "
        ret += f" last_Piece: {self.last_piece.symbol() if self.last_piece else ""}, "
        ret += f" captured_piece: {self.captured_piece.symbol() if self.captured_piece else ""}, "
        ret += f"checkers: [{",".join([str(c) for c in self.checkers])}] "
        ret += f"attacked_by_black: [{",".join([str(c) for c in self.attacked_by_black])}] "
        ret += f"attacked_by_white: [{",".join([str(c) for c in self.attacked_by_white])}] "
        return ret

class SmartChessBoard(EventDispatcher):
    """Tkinter display for chess game that extends chess.board """

    TK_LEFT_CLICK:str = "<Button-1>"
    TK_DOUBLE_CLICK:str = "<Double-Button-1>"

    def __init__(self, canvas:tk.Canvas, 
                 pieces_map:dict[str, str], 
                 fen: str | None = STARTING_FEN, *,
                 show_pieces:bool = True,
                 show_algebraic:bool=False,) -> None:        
        
        EventDispatcher.__init__(self)
        self._canvas = canvas
        self._canvas.bind(self.TK_LEFT_CLICK, self._left_mouse_click)
        self._canvas.bind(self.TK_DOUBLE_CLICK, self._double_click)
        self._square_size:int = int(canvas.cget("width")) // 8

        self._image_map:dict[str, ImageTk.PhotoImage] = load_pieces(pieces_map,
                                                                    self._square_size)

        self._selected_square:Optional[Square]|None = None        
        self._show_algebraic:bool = show_algebraic
        self._show_pieces: bool = show_pieces

        self._board:Board = Board(fen)
        self._square_to_piece_map:dict[Square, Optional[int]] = {}        
        for s in SQUARES:
            self._square_to_piece_map[s] = None
        
        self._initialize()
             
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

    @property
    def chess_board(self)->Board:
        return self._board
    
    # region public methods
    
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
        return [m.to_square for m in self._board.legal_moves if m.from_square == sq]

    def process_move(self, move:Move)->bool:
        print(f"Move: from {move.from_square}, to {move.to_square}")
        p:Piece | None = self._board.piece_at(move.from_square)
        
        if not self._board.is_legal(move) or p is None:
            return False
        
        self.clear_display_cues()
        self.push(move)

        return True

    def clear_display_cues(self):
        self._clear_legal_squares()
        self.set_selected_square(None)

    def set_display_cues(self):
        ...

    def get_squares_by_chess_color(self, color:Color)->dict[Square, Piece]:
        squares:dict[Square, Piece] = {}
        for sq in SQUARES:
            p:Piece|None = self._board.piece_at(sq)

            if p is not None:
                if p.color == color:
                    squares[sq] = p

        return squares

    def get_board_status(self)->BoardStatus:
        last:Move = self._board.pop()
        b_stat:BoardStatus = BoardStatus(last_move=last, turn=self._board.turn) 

        b_stat.last_piece = self._board.piece_at(last.from_square)     
        b_stat.captured_piece = self._board.piece_at(last.to_square)
        b_stat.selected_square = self._selected_square
        self._board.push(last)

        b_stat.is_game_over = self._board.is_game_over()

        if not b_stat.is_game_over:
            for c in [WHITE,BLACK]:
                for k,v in self.get_squares_by_chess_color(c).items():
                    for asq in list(self._board.attackers(BLACK if c == WHITE else WHITE, k)):
                        att_p:Piece|None = self._board.piece_at(asq)
                        if att_p is not None:
                            if c == WHITE:
                                b_stat.attacked_by_black.append(Attack(asq, k, att_p, v))
                            else:
                                b_stat.attacked_by_white.append(Attack(asq, k, att_p, v))

            for ck in list(self._board.checkers()):
                k:Square|None = self._board.king(self._board.turn)
                att_p:Piece|None = self._board.piece_at(ck)
                if k is not None and att_p is not None:
                    b_stat.checkers.append(Attack(ck, k, att_p, Piece(KING, self._board.turn)))
                
        return b_stat    

    # region endregion

    # region Wrapped chess.board methods

    def set_piece_at(self, square:Square, piece:Piece|None, promoted:bool=False)->None:
        self._remove_piece_display(square)
        self._set_piece_display(square, piece)

        self._board.set_piece_at(square, piece, promoted)
   
    def remove_piece_at(self, square:Square)->Piece|None:
        self._remove_piece_display(square)
        return self._board.remove_piece_at(square)

    def reset(self):
        self._remove_all_pieces_display()
        self._board.reset()
        self._set_all_pieces_display()

    def push(self, move: Move) -> None:
        self._remove_piece_display(move.from_square)
        self._set_piece_display(move.to_square, self._board.piece_at(move.from_square))
        self._board.push(move)
        self.set_moves_squares(move)

    def pop(self)->Move: 
        piece:Optional[Piece] = self._board.piece_at(self._board.peek().to_square)
        mv:Move = self._board.pop()

        self._remove_piece_display(mv.to_square)
        if piece is not None:
            self._set_piece_display(mv.from_square,piece)

        return mv

    def fen(self, *, shredder: bool = False, en_passant: Literal['legal'] | Literal['fen'] | Literal['xfen'] = "legal", promoted: bool | None = None) -> str:
        return self._board.fen(shredder=shredder, en_passant=en_passant, promoted=promoted)

    def set_fen(self, fen: str) -> None:
        self.clear_board_display()
        self._board.set_fen(fen)
        self._set_all_pieces_display()

    def piece_at(self, square:Square)->Piece|None:
        return self._board.piece_at(square)

    @property
    def turn(self):
        return self._board.turn

    #endregion

    # region private methods

    def _clear_legal_squares(self):
        self._canvas.delete(LEGAL_TAG)

    def _set_legal_square(self, sq:Square):
        mp:Optional[Piece] = self._board.piece_at(sq)
        if mp is not None:
            for square in self.get_legal_squares(sq):
                p:Optional[Piece] = self._board.piece_at(square)
                if p is None:
                    bb:list[float] = self._get_square_bbox(square)
                    self._canvas.create_oval(bb[0] + 4, bb[1] + 4, bb[2] -4, bb[3] - 4,
                                        width=0.0, fill=LEGAL, tags=LEGAL_TAG)
                else:
                    if p.color != mp.color:
                        print(f"from: {square_name(sq)}, to: {square_name(square)}")
                        fs:list[float] = self._get_square_bbox(sq)
                        ts:list[float] = self._get_square_bbox(square)
                        half:int = self._square_size // 2
                        self._canvas.create_line(fs[0] + half, fs[1] + half, ts[2] - half, ts[3] - half, arrow=tk.LAST, width=3, fill="red")
                        # sym:str = "a" + Piece.symbol(p)
                        # self._board._remove_piece_at(square)
                        # self._set_piece_image(sq, sym)
    
    def _left_mouse_click(self, event:tk.Event)->None:
        """
        user makes left click

        Args:
            event (tk.Event): event containing x, y coordinates
        """
        sq = self._get_square_click(event.x, event.y)
        data:dict[str, Any] = {"square":sq, "selected_square":self._selected_square}
        self._dispatch(Event.SQUARE_CLICK, data)

    def _double_click(self, event:tk.Event)->None:
        """
        user makes double click

        Args:
            event (tk.Event): event containing x, y coordinates
        """
        self._dispatch(Event.DOUBLE_CLICK, {"square":self._get_square_click(event.x, event.y)})     

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
        for l in PIECE_LETTERS:
            self._canvas.delete(l)

    def _set_all_pieces_display(self):
        for k, v in self._board.piece_map().items():
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

    def _get_square_click(self, x:int, y:int)->Square:
        file:int = math.floor(x / self._square_size)
        rank:int = 7 - math.floor(y / self._square_size)
        return square(file, rank)

#endregion