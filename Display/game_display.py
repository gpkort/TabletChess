import tkinter as tk
from typing import Any, Tuple, Callable
from PIL import Image, ImageTk
import chess
from chess import Board, engine
from GameManager import STARTING_FEN

import numpy as np

from Input import Event as DisplayEvent, EventDispatcher
SCREEN_WIDTH = SCREEN_HEIGHT = 512
BOARD_SIZE = 8

# Colors
WHITE:Tuple[int, int, int] = (255, 255, 255)
BLACK:Tuple[int, int, int] = (0, 0, 0)
LIGHT_SQUARE:Tuple[int, int, int] = (238, 238, 210)
DARK_SQUARE:Tuple[int, int, int] = (118, 150, 86)
SELECTED_SQUARE:Tuple[int, int, int] = (255, 255, 0)

LIGHT_SQUARE_COLOR = f"#{LIGHT_SQUARE[0]:x}{LIGHT_SQUARE[1]:x}{LIGHT_SQUARE[2]:x}"
DARK_SQUARE_COLOR = f"#{DARK_SQUARE[0]:x}{DARK_SQUARE[1]:x}{DARK_SQUARE[2]:x}"
SELECTED_SQUARE_COLOR = f"#{SELECTED_SQUARE[0]:x}{SELECTED_SQUARE[1]:x}{SELECTED_SQUARE[2]:X}"

ALLOWABLE_CHARS:str = "rnbqkpRNBQKP012345678w /-"
ROW_CHARS:str = "rnbqkpRNBQKP012345678"


class InvalidFenFormat(Exception):
    """Raised when a string containing Forsyth–Edwards Notation is invalid"""
class InvalidBoardFormat(Exception):
    """Raised when a string containing Forsyth–Edwards Notation is invalid"""

class SquareInfo:
    YELLOW:str = "#FFFF00"
    GREEN:str = "#785DB7"
    def __init__(self,
                 canvas:tk.Canvas,
                 name:str,
                 x:int,
                 y:int,
                 size:int,
                 *,
                 image:ImageTk.PhotoImage | None = None):

        self._canvas:tk.Canvas = canvas
        self._x:int = x
        self._y:int = y
        self._size = size
        self._image:ImageTk.PhotoImage | None = image
        self._name:str = name
        self._image_id:int = -1
        self._rect_id:int = -1
        self._circ_id:int = -1

    @property
    def name(self):
        """ 
            gets algebraic name of square
        Returns:
            str: name
        """
        return self._name
    @property
    def x(self)->int:
        return self._x
    @property
    def y(self)->int:
        return self._y
    @property
    def image(self) -> ImageTk.PhotoImage | None:
        return self._image
    @property
    def selected(self) -> bool:
        return self._rect_id != -1
    @selected.setter
    def selected(self, value:bool):
        if value == self._rect_id != -1:
            return

        if value:
            self._rect_id = self._canvas.create_rectangle(self._x,
                                          self._y,
                                          self._x + self._size,
                                          self._y + self._size,
                                          width=2,
                                          outline=self.YELLOW
                                          )
        else:
            self._canvas.delete(self._rect_id)
            self._rect_id = -1


    @property
    def legal(self)-> bool:
        return self._circ_id != -1    
    @legal.setter
    def legal(self, value:bool):
        if value == self._circ_id != -1:
            return
        if value:
            self._circ_id = self._canvas.create_oval(self._x + 4,
                                          self._y + 4,
                                          self._x + self._size - 8,
                                          self._y + self._size - 8,
                                          width=0.0,
                                          fill=self.GREEN)
        else:
            self._canvas.delete(self._circ_id)
            self._circ_id = -1
    
    def show_image(self):
        if self._image_id != -1:
            self._canvas.delete(self._image_id)
            self._image_id = -1

        # pylint: disable=pointless-statement
        self._image_id = self._canvas.create_image(self.x + 2,
                                                self.y + 2,
                                                anchor=tk.NW,
                                                image=self._image)

    def set_image(self, img:ImageTk.PhotoImage, show:bool = False):
        self._image = img
        self._image_id = -1
        if show:
            self.show_image()
    
    def kill(self)->ImageTk.PhotoImage | None:
        if self._image_id != -1:
            self._canvas.delete(self._image_id)
            self._image_id = -1

        tempImage:ImageTk.PhotoImage | None = self._image
        self._image = None

        return tempImage

class BoardDisplay(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, root: tk.Tk,
                 width: int,
                 height: int,
                 pieces_map:dict[str, str],
                 engine: engine.SimpleEngine,
                 *,
                 is_single_player:bool = True,
                 single_player_is_white:bool = True,
                 initial_setup:str | None = None,
                 rotation: int = 0):

        super().__init__()
        self.width = width
        self.height = height
        self.rotation = 0
        self.square_size:int = self.width // BOARD_SIZE
        self.is_single_player:bool = is_single_player
        self.player_color:chess.Color = chess.WHITE if single_player_is_white else chess.BLACK

        self.root: tk.Tk = root
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.width) #make it square
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.dispatchButton)

        self.engine = engine
        self.board:Board = Board()
        self.selected_square:chess.Square|None = None

        self.board_display:dict[chess.Square, SquareInfo] = {}
        self.background_img:ImageTk.PhotoImage | None = None  
        self.image_map:dict[str, ImageTk.PhotoImage] = self._load_pieces(pieces_map) 
        self._initialize()

    def _load_pieces(self, pieces_map:dict[str, str]) -> dict[str, ImageTk.PhotoImage]:
        """stores images into map

        Args:
           piece_map (dict[str, str]) : A map contining the piece abbreviation and the path to the image

        Returns:
            None
        """
        
        images:dict[str, ImageTk.PhotoImage] = {}

        for k,v in pieces_map.items():
            image = Image.open(v)

            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image = image.resize((self.square_size - 4, self.square_size - 4))

            pixs = np.array(image)            
            r, g, b, a = pixs[:,:,0], pixs[:,:,1], pixs[:,:,2], pixs[:,:,3]
            white = (r==255) & (g== 55) & (b==225)
            pixs[..., 3] = np.where(white, 0, a)
            images[k] = ImageTk.PhotoImage(Image.fromarray(pixs))

        return images

    def dispatchButton(self, event:tk.Event):
        square:chess.Square | None = self.get_square(event.x, event.y)
        if square is None:
            return

        self.handle_square_selection(square)

    def new_game(self):
        self.board.reset()
        self.update_board_display()        
    
    def handle_square_selection(self, square:chess.Square):
        if self.board.is_game_over():
            return
        
        if self.selected_square is None:
            piece:chess.Piece | None = self.board.piece_at(square)
            if piece is None or piece.color != self.board.turn:
                return
            self.display_legal_moves(square, piece)
            self.set_selected_square(square)
        else:
            if self.selected_square == square:
                self.clear_board_squares()
            else:
                piece:chess.Piece | None = self.board.piece_at(self.selected_square)
                if piece is None or piece.color != self.board.turn:
                    return
                moves:list[chess.Move] = self.get_legal_moves(self.selected_square)
                for m in moves:
                    if m.to_square == square:
                        self.move_piece(self.selected_square, square)
                        self.update_board_display()

    def update_board_display(self):
        # for key, val in self.board_display.items():
            
        # self.update_root_display

        for key, val in self.board_display.items():
            val.kill()
            val.legal = False
            val.selected = False

            piece:chess.Piece | None = self.board.piece_at(key)
            if piece:
                sym:str = piece.symbol()
                self.board_display[key].set_image(self.image_map[sym], True)

        self.selected_square = None
        self.update_root_display

    def display_legal_moves(self, square:chess.Square, piece:chess.Piece):        
        self.clear_board_squares(selected=False)                
        moves:list[chess.Move] = self.get_legal_moves(square)

        for m in moves:
            self.board_display[m.to_square].legal = True

        self.update_root_display()

    def move_piece(self, from_square:chess.Square, to_square:chess.Square)->bool:
        move = chess.Move(from_square, to_square)
        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def set_selected_square(self, square:chess.Square):
        if(self.selected_square == square):
            return
        
        self.board_display[square].selected = True
        self.selected_square = square
        self.update_root_display()

    def get_legal_moves(self, square:chess.Square)-> list[chess.Move]:
        moves:list[chess.Move] = [m for m in self.board.legal_moves if m.from_square == square ]
        
        return moves

    def clear_board_squares(self, *, legal:bool=True, selected:bool=True):
        for sq in self.board_display.values():
            if selected:
                sq.selected = False
            if legal:
                sq.legal = False
        if selected:
            self.selected_square = None

        self.update_root_display()
    
    def get_square(self, x:int, y:int)->chess.Square|None:
        for k, val in self.board_display.items():
            if val.x <= x <= val.x + self.square_size and val.y <= y <= val.y + self.square_size:
                return k
    
    def _dispatch(self, event:DisplayEvent, data: dict[str, Any] | None = None): # pylint: disable=unused-argument
        ...

    def _initialize(self):
        """
        Initializes self.board_display_map and creates a background image

        Returns:
           ImageTk.PhotoImage: background image
           
        Raises:
            Exception if self.board_display was initialized with 64 values
        """
        self.board_display = {}
        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                color:str = LIGHT_SQUARE_COLOR if (rank + file) % 2 == 0 else DARK_SQUARE_COLOR
                x0:int = file * self.square_size
                y0:int = rank * self.square_size
                x1:int = x0 + self.square_size
                y1:int = y0 + self.square_size

                name:str = chess.square_name(chess.square(7 - file, 7 - rank))
                square:chess.Square = chess.parse_square(name)
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                self.board_display[square] = SquareInfo(self.canvas, 
                                                      name, 
                                                      x0, 
                                                      y0, 
                                                      self.square_size)


    def display_image(self, img: ImageTk.PhotoImage, x_pos:int=0, y_pos:int=0):
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=img)
        self.update_display

    def update_root_display(self):
        self.root.update_idletasks()
        self.root.update()  

