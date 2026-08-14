from dataclasses import dataclass, field
from typing import Tuple, Any, Optional, override
import math

import tkinter as tk
from PIL import ImageTk, Image
from chess import (STARTING_FEN, Square, 
                   square, 
                   SQUARES, 
                   square_rank, 
                   square_file, 
                   square_name,
                   Piece,
                   Board)
import numpy as np

from Input import EventDispatcher, Event
from . import load_pieces_to_map

LIGHT_SQUARE:Tuple[int, int, int] = (238, 238, 210)
DARK_SQUARE:Tuple[int, int, int] = (118, 150, 86)
SELECTED_SQUARE:Tuple[int, int, int] = (255, 255, 0)

LIGHT_SQUARE_COLOR = f"#{LIGHT_SQUARE[0]:x}{LIGHT_SQUARE[1]:x}{LIGHT_SQUARE[2]:x}"
DARK_SQUARE_COLOR = f"#{DARK_SQUARE[0]:x}{DARK_SQUARE[1]:x}{DARK_SQUARE[2]:x}"
# SELECTED_SQUARE_COLOR = f"#{SELECTED_SQUARE[0]:x}{SELECTED_SQUARE[1]:x}{SELECTED_SQUARE[2]:X}"
SELECTED_SQUARE_COLOR:str ="#FFFF00"
TO_FROM_SQUARE_COLOR:str = "#64B7DA"
CIRCLE_COLOR:str = "#083808"

@dataclass
class SquareState:
    selected:bool = False
    is_to_square:bool = False
    is_from_square:bool = False

@dataclass
class SquareData:
    background_id:int = -1
    piece_id:int = -1
    label_id:int = -1
    bbox:list[float] = field(default_factory=list)    

@dataclass
class ChessBoardInfo:
    selected_square:Square|None = None
    from_square:Square|None = None
    to_square:Square|None = None

class ChessBoard(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, canvas:tk.Canvas, pieces_map:dict[str, str],*, show_algebraic:bool=False):                

        super().__init__()
        self._canvas = canvas
        self._canvas.bind(self.TKINTER_LEFT_CLICK, self._left_mouse_click)
        self._square_size:int = int(canvas.cget("width")) // 8   

        self._board_map:dict[Square, SquareData] = {}
        for s in SQUARES:
            self._board_map[s] = SquareData()    
        self._image_map:dict[Piece, ImageTk.PhotoImage] = load_pieces_to_map(pieces_map, self._square_size)

        self._selected_square:Tuple[Square, int]|None = None
        self._dotted_squares:list[Tuple[Square, int]] = []
        self._from_square:Square|None = None
        self._to_square:Square|None = None

        self._show_algebraic:bool = show_algebraic
        self._initialize()
    
    @property
    def pieces(self)->dict[Square, Piece]:
        pm:dict[Square, Piece] = {}
        for k, v in self._board_map.items():
            if v.piece is not None:
                pm[k] = v.piece
        return pm
    @pieces.setter
    def pieces(self, piece_map:dict[Square, Piece]):
        for k, v in piece_map.items():
            self.set_piece(k, v)
    
    def get_piece_at(self, sq:Square)->Piece|None:
        return None
    
    def _left_mouse_click(self, event:tk.Event):
            """
            user makes left click
    
            Args:
                event (tk.Event): event containing x, y coordinates
            """
            file:int = math.floor(event.x / self._square_size)
            rank:int = 7 - math.floor(event.y / self._square_size)
            sq:Square = square(file, rank)
            data:dict[str, Any] = {"data":{"square":sq, "state":self.get_square_state(sq)}}
            self._dispatch(Event.SQUARE_CLICK, data) 

    def load_pieces(self, pieces_map:dict[str, str]) -> dict[Piece, ImageTk.PhotoImage]:
        """stores images into map
        Args:
            piece_map (chess.Piece[str, str]) : converts file paths to tkinter images

        Returns:
            dict[chess.Piece, ImageTk.PhotoImage]
        """
    
        images:dict[Piece, ImageTk.PhotoImage] = {}

        for k,v in pieces_map.items():
            p:Piece = Piece.from_symbol(k)

            image = Image.open(v)

            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image = image.resize((self._square_size - 4, self._square_size - 4))

            pixs = np.array(image)            
            r, g, b, a = pixs[:,:,0], pixs[:,:,1], pixs[:,:,2], pixs[:,:,3]
            white = (r==255) & (g== 55) & (b==225)
            pixs[..., 3] = np.where(white, 0, a)
            images[p] = ImageTk.PhotoImage(Image.fromarray(pixs))

        return images

    def _initialize(self):
        """
        Initializes self._board_map_map and creates a background image

        Returns:
            list[list[int]]:
            
        Raises:
            Exception if self._board_map was initialized with 64 values
        """
        self._algebraic_ids = []
        for sq in SQUARES:
            f = square_file(sq)
            r = 7 - square_rank(sq)
            color:str = LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
            x0:int = f * self._square_size
            y0:int = r * self._square_size
            x1:int = x0 + self._square_size
            y1:int = y0 + self._square_size

            self._board_map[sq] = SquareData()
            self._board_map[sq].background_id = self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=3)            
            self._board_map[sq].label_id = self._canvas.create_text(x0 + 7, y1-7, text=square_name(sq), 
                                                            fill="red", font=("Arial", 8, "bold"),
                                                            state=('normal' if self._show_algebraic else 'hidden'))
            self._board_map[sq].bbox = [x0, y0, x1, y1]

    def move_piece(self, from_sq:Square, to_sq:Square, show_move:bool=False):
        if self._board_map[from_sq].has_piece:
            sd:SquareData = self.clear_piece_square(from_sq)
            if sd.piece is not None:
                self.set_piece(to_sq, sd.piece) #type ignore

            if(show_move):
                self.clear_to_from_squares()
                self.update_to_from_squares(from_sq, to_sq)

    def set_piece(self, sq:Square, piece:Piece):
        self.clear_piece_square(sq)
        coords = coords = self._board_map[sq].bbox
        self._board_map[sq].piece_id = self._canvas.create_image(coords[0] + 2, coords[1] + 2,
                                                                anchor=tk.NW, image=self._image_map[piece])
        self._board_map[sq].piece = piece             
    
    def clear_piece_square(self, sq:Square)->SquareData:
        sd:SquareData = SquareData()

        if self._board_map[sq].has_piece:
            self._canvas.delete(self._board_map[sq].piece_id)
            sd.piece_id= self._board_map[sq].piece_id
            sd.piece=self._board_map[sq].piece
            self._board_map[sq].piece_id = -1
            self._board_map[sq].piece = None

        return sd

    def clear_pieces(self):
        for kp in self.pieces.keys():
            self.clear_piece_square(kp)
        
    def clear_board_display(self, *, clear_pieces:bool=True):
        self.selected_square = None
        self.to_square = None
        self.from_square = None 
        self.dotted_squares = None       

        if clear_pieces:
            for k in self._board_map.keys():
                self.clear_piece_square(k)
    
    def update_board_display(self, display_info:ChessBoardInfo, clear_board:bool = True):
            """
            Iterates through squares and updates visual
            representation
            """
            if clear_board:
                self.clear_board_display()            
            
            self.selected_square = display_info.selected_square 
            self.to_square = display_info.to_square
            self.from_square = display_info.from_square
            self.dotted_squares = display_info.legal_squares
            
            for square, piece in display_info.piece_location.items():
                self.set_piece(square, piece)
                   
    

class SmartChessBoard(Board, EventDispatcher):
    """Tkinter display for chess game that extends chess.board """

    TKINTER_LEFT_CLICK:str = "<Button-1>"
    def __init__(self, canvas:tk.Canvas, 
                 pieces_map:dict[str, str], 
                 fen: str | None = STARTING_FEN, *,
                 show_pieces:bool = True,
                 chess960: bool = False,
                 show_algebraic:bool=False,
                 show_legal_move:bool = True) -> None:
        super().__init__(fen, chess960=chess960)

        self._canvas = canvas
        self._canvas.bind(self.TKINTER_LEFT_CLICK, self._left_mouse_click)
        self._square_size:int = int(canvas.cget("width")) // 8   

        # self._board_map:dict[Square, SquareData] = {}
        # for s in SQUARES:
        #     self._board_map[s] = SquareData()    
        self._image_map:dict[Piece, ImageTk.PhotoImage] = load_pieces_to_map(pieces_map, self._square_size)
        
        self._selected_square:Tuple[Square, int]|None = None
        self._dotted_squares:list[Tuple[Square, int]] = []
        self._from_square:Optional[Square] = None
        self._to_square:Optional[Square] = None

        self._show_algebraic:bool = show_algebraic
        self._show_pieces: bool = show_pieces
        self._initialize(show_pieces)\

    @property
    def board_info(self)->ChessBoardInfo:
        return ChessBoardInfo(selected_square=self.selected_square,
                                from_square=self._from_square,
                                to_square=self._to_square)
    @property
    def selected_square(self)->Square|None:
            return self._selected_square[0] if self._selected_square is not None else None
    @selected_square.setter
    def selected_square(self, sq:Square|None):
        if self._selected_square is not None:
                self._canvas.delete(self._selected_square[1])
                self._selected_square = None
        if sq is not None:
            coords = self._board_map[sq].bbox
            self._selected_square = (sq, 
                                     self._canvas.create_rectangle(coords, fill="", 
                                                                    outline=SELECTED_SQUARE_COLOR,
                                                                    width=3))
    
    @property
    def to_square(self)->Square | None:
        return self._to_square
    @to_square.setter
    def to_square(self, sq:Square|None):
        if self._to_square is not None:
            self._canvas.itemconfig(self._board_map[self._to_square].background_id, 
                                        fill=self._get_square_color(self._to_square))
            self._to_square = None
        if sq is not None:
            self._canvas.itemconfig(self._board_map[sq].background_id, fill=TO_FROM_SQUARE_COLOR)
            self._to_square = sq
    
    @property
    def from_square(self)->Square | None:
        return self._from_square
    @from_square.setter
    def from_square(self, sq:Square|None):
        if self._from_square is not None:
            self._canvas.itemconfig(self._board_map[self._from_square].background_id, 
                                        fill=self._get_square_color(self._from_square))
            self._from_square = None
        if sq is not None:
            self._canvas.itemconfig(self._board_map[sq].background_id, fill=TO_FROM_SQUARE_COLOR)
            self._from_square = sq
    
    @property
    def show_algebraic(self)->bool:
        return self._show_algebraic
    @show_algebraic.setter
    def show_algebraic(self, show:bool):
        for val in self._board_map.values():
            self._canvas.itemconfigure(val.label_id, state=('normal' if show else 'hidden'))
        self._show_algebraic = show

    def get_square_state(self, sq:Square)->SquareState:
            return SquareState(selected= sq == self._selected_square,
                               is_from_square=sq == self._from_square,
                               is_to_square= sq == self._to_square)
    
    @override
    def set_piece_at(self, square:Square, piece:Piece|None, promoted:bool=False)->None:
        if piece is None:
            if self.piece_at(square):
                coords:list[float] = self._board_map[square].bbox
                self._board_map[square].piece_id = self._canvas.create_image(coords[0] + 2, coords[1] + 2,
                                                                    anchor=tk.NW, image=self._image_map[piece]) # type: ignore
            self.remove_piece_at(square)
        else:
            super().set_piece_at(square, piece, promoted)            

    @override
    def remove_piece_at(self, square:Square)->Piece|None:
        self._remove_piece_display_at(square)
        return super().remove_piece_at(square)

    @override
    def reset(self):
        for s in SQUARES:
            self._remove_piece_display_at(s)


    def _left_mouse_click(self, event:tk.Event):
            """
            user makes left click
    
            Args:
                event (tk.Event): event containing x, y coordinates
            """
            file:int = math.floor(event.x / self._square_size)
            rank:int = 7 - math.floor(event.y / self._square_size)
            sq:Square = square(file, rank)
            data:dict[str, Any] = {"data":{"square":sq, "state":self.get_square_state(sq)}}
            self._dispatch(Event.SQUARE_CLICK, data)

    def set_all_pieces(self):
        ...

    def _remove_piece_display_at(self, square:Square)->Piece|None:
            self._canvas.delete(self._board_map[square].piece_id)
            self._board_map[square].piece_id = -1

    def _initialize(self, show_pieces):
        """
        Initializes self._board_map_map and creates a background image
                    
        Raises:
            Exception if self._board_map was initialized with 64 values
        """
        self._algebraic_ids = []
        for sq in SQUARES:
            f = square_file(sq)
            r = 7 - square_rank(sq)
            color:str = LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
            x0:int = f * self._square_size
            y0:int = r * self._square_size
            x1:int = x0 + self._square_size
            y1:int = y0 + self._square_size

            self._canvas.create_rectangle(x0, y0, x1, y1,
                                        tags=f"{square_name(sq)}_bg",
                                        fill=self._get_square_color(sq), 
                                        width=3)            
            self._canvas.create_text(x0 + 7, y1-7, text=square_name(sq), 
                                    fill="red", font=("Arial", 8, "bold"),
                                    state=('normal' if self._show_algebraic else 'hidden'))
    def _get_square_bbox(self, square:Square) ->list[float]:
        """
        helper to square coordinates
        """
        return self._canvas.coords(f"{square_name(square)}_bg")
        
    def _get_square_color(self, sq:Square)->str:
        """
        handy util to get background color
        """
        return LIGHT_SQUARE_COLOR if (square_rank(sq) + square_file(sq)) % 2 == 0 else DARK_SQUARE_COLOR

        

    
                
    