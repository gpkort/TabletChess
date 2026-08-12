from dataclasses import dataclass, field
from typing import Any, Tuple
from enum import Enum

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import ImageTk, Image
import chess
import numpy as np

from Input import EventDispatcher, Event

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
class SquareData:
    background_id:int = -1
    piece_id:int = -1
    label_id:int = -1
    piece_str:str = ""
    bbox:list[float] = field(default_factory=list)

@dataclass
class ChessBoardInfo:
    selected_square:chess.Square|None = None
    previous_square:chess.Square|None = None
    target_square:chess.Square|None = None
    legal_squares:list[chess.Square] = field(default_factory=list)
    piece_location:dict[chess.Square, str] = field(default_factory=dict)

class ChessBoard(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, canvas:tk.Canvas, pieces_map:dict[str, str],*, show_algebraic:bool=False):                

        super().__init__() 
        self._canvas = canvas
        self._square_size:int = int(canvas.cget("width")) // 8   

        #A multi-dimmension array to  represent board list[file][rank]
        self._board_map:dict[chess.Square, SquareData] = {}
        
        self._image_map:dict[str, ImageTk.PhotoImage] = self.load_pieces(pieces_map)
        # self._piece_ids:list[int] = []        

        self._selected_square:Tuple[chess.Square, int]|None = None
        self._dotted_squares:list[Tuple[chess.Square, int]] = []
        self._previous_square:chess.Square|None = None
        self._target_square:chess.Square|None = None

        self._show_algebraic:bool = show_algebraic
        # self._algebraic_ids:list[int] = []  
        self._initialize()   

    @property
    def highlighted_square(self)->chess.Square|None:
         return self._selected_square[0] if self._selected_square is not None else None
         
    @property
    def dotted_squares(self)->list[chess.Square]:
        return [val[0] for val in self._dotted_squares]

    @property
    def target_square(self)->chess.Square | None:
        return self._target_square
    @property
    def previous_square(self)->chess.Square | None:
        return self._previous_square

    def show_algebraic(self, show:bool):
        for val in self._board_map.values():
            self._canvas.itemconfigure(val.label_id, state=('normal' if show else 'hidden'))
        self._show_algebraic = show
    
    def _left_mouse_click(self, event:tk.Event):
            """
            user makes left click
    
            Args:
                event (tk.Event): event containing x, y coordinates
            """
            print(f"X: {event.x}, Y: {event.y}")

    def load_pieces(self, pieces_map:dict[str, str]) -> dict[str, ImageTk.PhotoImage]:
        """stores images into map
        Args:
            piece_map (chess.Piece[str, str]) : converts file paths to tkinter images

        Returns:
            dict[chess.Piece, ImageTk.PhotoImage]
        """
    
        images:dict[str, ImageTk.PhotoImage] = {}

        for k,v in pieces_map.items():
            image = Image.open(v)

            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image = image.resize((self._square_size - 4, self._square_size - 4))

            pixs = np.array(image)            
            r, g, b, a = pixs[:,:,0], pixs[:,:,1], pixs[:,:,2], pixs[:,:,3]
            white = (r==255) & (g== 55) & (b==225)
            pixs[..., 3] = np.where(white, 0, a)
            images[k] = ImageTk.PhotoImage(Image.fromarray(pixs))

        return images

    def _initialize(self):
        """
        Initializes self._board_map_map and creates a background image

        Returns:
            list[list[int]]:
            
        Raises:
            Exception if self._board_map was initialized with 64 values
        """
        self._board_map = {}
        self._piece_ids = []
        self._algebraic_ids = []
        for sq in chess.SQUARES:
            f = chess.square_file(sq)
            r = 7 - chess.square_rank(sq)
            color:str = LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
            x0:int = f * self._square_size
            y0:int = r * self._square_size
            x1:int = x0 + self._square_size
            y1:int = y0 + self._square_size

            self._board_map[sq] = SquareData()
            self._board_map[sq].background_id = self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=3)            
            self._board_map[sq].label_id = self._canvas.create_text(x0 + 7, y1-7, text=chess.square_name(sq), 
                                                            fill="red", font=("Arial", 8, "bold"),
                                                            state=('normal' if self._show_algebraic else 'hidden'))
            self._board_map[sq].bbox = [x0, y0, x1, y1]

    def move_piece(self, from_sq:chess.Square, to_sq:chess.Square, show_move:bool=False):
        if self._board_map[from_sq].piece_id != -1 and self._board_map[from_sq].piece_str != "":
            sd:SquareData = self.clear_piece_square(from_sq)
            self.place_piece_square(to_sq, sd.piece_str)

            if(show_move):
                self.clear_to_from_squares()
                self.update_to_from_squares(from_sq, to_sq)

    def place_piece_square(self, sq:chess.Square, piece:str):
        self.clear_piece_square(sq)
        coords = coords = self._board_map[sq].bbox
        self._board_map[sq].piece_id = self._canvas.create_image(coords[0] + 2, coords[1] + 2,
                                                                anchor=tk.NW, image=self._image_map[piece])
        self._board_map[sq].piece_str = self._board_map[sq].piece_str = piece                

    def clear_to_from_squares(self):
        if self._target_square is not None:
            self._canvas.itemconfig(self._board_map[self._target_square].background_id, 
                                        fill=self._get_square_color(self._target_square))
            self._target_square = None
        if self._previous_square is not None:
            self._canvas.itemconfig(self._board_map[self._previous_square].background_id, 
                                    fill=self._get_square_color(self._previous_square))
            self._previous_square = None

    def clear_piece_square(self, sq:chess.Square)->SquareData:
        sd:SquareData = SquareData()

        if self._board_map[sq].piece_id != -1 and self._board_map[sq].piece_str != "":
            self._canvas.delete(self._board_map[sq].piece_id)
            sd.piece_id= self._board_map[sq].piece_id
            sd.piece_str=self._board_map[sq].piece_str
            self._board_map[sq].piece_id = -1
            self._board_map[sq].piece_str = ""

        return sd

    def clear_board_display(self):
        if self._selected_square is not None:
            self._canvas.delete(self._selected_square[1])
            self._selected_square = None

        self.clear_to_from_squares() 

        for ds in self._dotted_squares:
            self._canvas.delete(ds[1])

        for k in self._board_map.keys():
            self.clear_piece(k)
    
    def update_to_from_squares(self, previous:chess.Square|None, target:chess.Square|None):
        if target is not None:
            self._canvas.itemconfig(self._board_map[target].background_id, fill=TO_FROM_SQUARE_COLOR)
            self._target_square = target
        if previous is not None:
            self._canvas.itemconfig(self._board_map[previous].background_id, fill=TO_FROM_SQUARE_COLOR)
            self._previous_square = previous

    def update_board_display(self, display_info:ChessBoardInfo):
            """
            Iterates through squares and updates visual
            representation
            """
            coords:list[float] = []
            self.clear_board_display()
            
            if display_info.selected_square is not None:
                coords = self._board_map[display_info.selected_square].bbox
                self._selected_square = (display_info.selected_square,
                                         self._canvas.create_rectangle(coords, fill="", 
                                                                       outline=SELECTED_SQUARE_COLOR,width=3))
                
            self.update_to_from_squares(display_info.previous_square, display_info.target_square)

            for lp in display_info.legal_squares:                
                coords = self._board_map[lp].bbox
                self._dotted_squares.append((lp, self._canvas.create_oval(coords[0] + 10, coords[1] + 10,
                                                                          coords[2] - 10, coords[3] - 10,
                                                                          fill=CIRCLE_COLOR)))
            for square, piece_str in display_info.piece_location.items():
                self.place_piece_square(square, piece_str)
                            
    def _get_square_color(self, sq:chess.Square)->str:
        f = chess.square_file(sq)
        r = chess.square_rank(sq)
        return LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
                
    