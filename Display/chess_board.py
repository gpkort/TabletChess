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

    def __init__(self, canvas:tk.Canvas, pieces_map:dict[str, str]):                

        super().__init__() 
        self._canvas = canvas
        self._square_size:int = int(canvas.cget("width")) // 8   

        #A multi-dimmension array to  represent board list[file][rank]
        self._board_display:dict[chess.Square, int] = {}
        
        self._image_map:dict[str, ImageTk.PhotoImage] = self.load_pieces(pieces_map )
        self._initialize()

        self._selected_square:Tuple[chess.Square|None, int|None] = (None, None)
        self._dotted_squares:list[Tuple[chess.Square|None, int|None]] = []
        self._to_from_squares:Tuple[Tuple[chess.Square|None, int|None],Tuple[chess.Square|None, int|None]] = ((None, None), (None, None))

    @property
    def highlighted_square(self)->chess.Square|None:
         return self._selected_square[0]
         
    @property
    def dotted_squares(self)->list[chess.Square|None]:
        return [val[0] for val in self._dotted_squares]

    @property
    def to_from_squares(self)->Tuple[chess.Square|None, chess.Square|None] | None:
         return (self._to_from_squares[0][0], self._to_from_squares[1][0])

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
            Initializes self._board_display_map and creates a background image
    
            Returns:
               list[list[int]]:
               
            Raises:
                Exception if self._board_display was initialized with 64 values
            """
            self._board_display = {}
            for sq in chess.SQUARES:
                 f = chess.square_file(sq)
                 r = chess.square_rank(sq)
                 color:str = LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
                 x0:int = f * self._square_size
                 y0:int = r * self._square_size
                 x1:int = x0 + self._square_size
                 y1:int = y0 + self._square_size
                 self._board_display[sq] = self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=3)
                 
            # for f in range(8):
            #     for r in range(8):
            #         color:str = LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
            #         x0:int = f * self._square_size
            #         y0:int = r * self._square_size
            #         x1:int = x0 + self._square_size
            #         y1:int = y0 + self._square_size
                    
            #         self._board_display[].append(self._canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=3))
            #     self._board_display.append(file_list)

    def update_board_display(self, display_info:ChessBoardInfo):
            """
            Iterates through squares and updates visual
            representation
            """

            if self._selected_square[1] is not None:
                self._canvas.delete(self._selected_square[1])
            self._selected_square = (None, None)

            if display_info.selected_square is not None:
                coords:list[float] = self._canvas.coords(self._board_display[display_info.selected_square])
                self._selected_square = (display_info.selected_square,
                                         self._canvas.create_rectangle(coords, fill="", outline=SELECTED_SQUARE_COLOR,width=3))
                      
                           
                           
    
            # for key, val in self._board_display.items():
            #     val.clear()
    
            # for square, piece_str in display_info.piece_location.items():
            #     self._board_display[square].set_image(self._image_map[piece_str], True)
    
            # if display_info.selected_square:
            #     self._board_display[display_info.selected_square].selected = True
            # if display_info.previous_square:
            #     self._board_display[display_info.previous_square].show_move = True
            # if display_info.target_square:
            #     self._board_display[display_info.target_square].show_move = True
            # for legal in display_info.legal_squares:
            #     self._board_display[legal].legal = True
    
            # self.update_root_display()
                
    