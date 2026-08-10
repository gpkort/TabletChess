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
SELECTED_SQUARE_COLOR = f"#{SELECTED_SQUARE[0]:x}{SELECTED_SQUARE[1]:x}{SELECTED_SQUARE[2]:X}"


class ChessBoard(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, canvas:tk.Canvas, pieces_map:dict[str, str]):                

        super().__init__() 

        self._canvas:tk.Canvas = canvas       
        self._square_size:int = int(self._canvas.cget("width")) // 64 #64 squares on a chess board    
        print(self._square_size)            
        
        self._image_map:dict[str, ImageTk.PhotoImage] = self.load_pieces(pieces_map )
        self._initialize()

        self._highlight_square:chess.Square|None = None
        self._dotted_squares:list[chess.Square] = []
        self._to_from_squares:Tuple[chess.Square, chess.Square] | None = None

    @property
    def highlighted_square(self)->chess.Square|None:
         return self._highlight_square
         
    @property
    def dotted_squares(self)->list[chess.Square]:
        return self._dotted_squares.copy()

    @property
    def to_from_squares(self)->Tuple[chess.Square, chess.Square] | None:
         return (self._to_from_squares[0], self._to_from_squares[1]) if self._to_from_squares is not None else None

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
            self._board_display = []
            for f in range(8):
                file_list:list[int]  = []
                for r in range(8):
                    color:str = LIGHT_SQUARE_COLOR if (r + f) % 2 == 0 else DARK_SQUARE_COLOR
                    x0:int = f * self._square_size
                    y0:int = r * self._square_size
                    x1:int = x0 + self._square_size
                    y1:int = y0 + self._square_size
                    
                    file_list.append(self._canvas.create_rectangle(x0, y0, x1, y1, fill=color))
                self._board_display.append(file_list)

            print(f"{len(self._board_display)} X {len(self._board_display[0])}")
           
            # for file in self._board_display:
            #      print(" ".join([str(i) for i in file]))
                
    