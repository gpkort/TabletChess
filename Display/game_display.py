import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from enum import Enum
from typing import Any, Tuple
import numpy as np
from dataclasses import dataclass
from typing import Tuple

from GameManager import STARTING_FEN, IMAGE_MAP

class Event(Enum):
    NEW = 1

SCREEN_WIDTH = SCREEN_HEIGHT = 512
BOARD_SIZE = 8

# Colors
WHITE:Tuple[int, int, int] = (255, 255, 255)
BLACK:Tuple[int, int, int] = (0, 0, 0)
LIGHT_SQUARE:Tuple[int, int, int] = (238, 238, 210)
DARK_SQUARE:Tuple[int, int, int] = (118, 150, 86)
SELECTED_SQUARE_COLOR:Tuple[int, int, int] = (255, 255, 0)

ALLOWABLE_CHARS:str = "rnbqkpRNBQKP012345678w /-"
ROW_CHARS:str = "rnbqkpRNBQKP012345678"


class InvalidFenFormat(Exception):
    """Raised when a string containing Forsyth–Edwards Notation is invalid"""
class InvalidBoardFormat(Exception):
    """Raised when a string containing Forsyth–Edwards Notation is invalid"""

class SquareInfo:
    def __init__(self, 
                 x:int, 
                 y:int, 
                 square_side:int,
                 id:int = -1,
                 image:ImageTk.PhotoImage | None = None,
                 selected:bool = False):
        
        self._x = x
        self._y = y
        self._square_side = square_side
        self._image:ImageTk.PhotoImage | None = image
        self._id = id
        self._selected:bool = selected
    
    @property
    def x(self)->int:
        return self._x
    @property
    def y(self)->int:
        return self._y
    @property
    def square_side(self)->int:
        return self._square_side
    @property
    def image(self) -> ImageTk.PhotoImage | None:
        return self._image
    @property
    def id(self) -> int:
        return self._id   #type: ignore 
    @id.setter
    def id(self, value:int):
        self._id = value
    @property
    def selected(self) -> bool:
        return self.selected
    @selected.setter
    def selected(self, value):
        self.selected = value        
        
    def set_image(self, img:ImageTk.PhotoImage):
        self.id = -1
        self._image = img
    
    def place(self, id:int, img:ImageTk.PhotoImage):
        self._id = int
        self._image = img
        
    def move(self)->Tuple[int, ImageTk.PhotoImage|None]:
        img = self._image
        id = self._id
        self._id = -1
        self._image = None
        return (id, img) # type: ignore
    
    def kill(self):
        self._id = -1
        self._image = None
    
    def is_hit(self, x:int, y:int)-> bool:
        return (self._x <= x <= self._x + self.square_side) and (self._y <= y <= self._y + self.square_side)
    
def validate_fen(fen:str):
    if not all(c in ALLOWABLE_CHARS for c in fen):
        raise InvalidFenFormat("Contains unallowed characters")
    if fen.split(" ")[0] is None:
        raise InvalidFenFormat("Does not contain row information")
    
    rows = (fen.split(" ")[0]).split("/")
    if len(rows) != 8:
        raise InvalidFenFormat(f"Does not information for all 8 rows {fen.split(" ")[0]}")
    
    for row in rows:
        if any(c not in ROW_CHARS for c in row):
            raise InvalidFenFormat(f"row: {row} contains invalid chars for piece placement")
        row_len = 0
        for p in row:
            if p.isdigit():
                row_len += int(p)
            else:
                row_len += 1
        if row_len != 8:
            raise InvalidFenFormat(f"Does row does not contain all information for 8 squares {row}")

def get_row_col(alg:str) -> Tuple[int, int] | None:
    lt:list[str] = [chr(i) for i in range(96, 105)]
    nu:list[str] = [str(i) for i in range(1, 9)]
    if len(alg) == 2 and (alg[0] in lt) and (alg[1] in nu):
        return (int(alg[1]), ord(alg[0])-96)
    
def get_algebraic(col:int, row:int)->str | None:
    """
    get square algebraic designation

    Args:
        col (int): Zero based col between 0 and 7 inclusive
        row (int): Zero based row between 0 and 7 inclusive
    Returns:
        str | None: ex a1, b4, etc or None row or col aren't valid
    """
    if (0 <= row <= 7) and (0 <= col <= 7):
        return chr(97 + col) + str(row + 1)

class BoardDisplay:
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, root: tk.Tk, 
                 width: int, 
                 height: int, 
                 pieces_map:dict[str, str], *,
                 initial_setup:str | None = None,
                 rotation: int = 0):
        
        self.width = width
        self.height = height
        self.rotation = 0
        self.square_size:int = self.width // BOARD_SIZE
                
        self.root: tk.Tk = root        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.width) #make it square
        self.canvas.pack(fill="both", expand=True)
        # self.canvas.bind(self.TKINTER_LEFT_CLICK, self.canvas_click)
        
        self.board:dict[str, SquareInfo] = {}
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

    def draw(self, fen:str):
        self._parse_fen(fen)      
        
        for square in self.board.values():
            square.id = self.canvas.create_image(square.x + 2, square.y + 2, anchor="nw", image=square.image)        

    def canvas_click(self, event):
        print(f"x = {event.x}; y = {event.y}")
        for key, square in self.board.items():
            if square.is_hit(event.x, event.y):
                print(f"{key} was hit")
    
    def validate_board(self):
        missing_keys:list[str] = []
        for l in range(97, 105):
            for i in range(1, 9):
                alg:str = chr(l) + str(i)
                print("TEST")
                if alg not in list(self.board.keys()):
                    missing_keys.append(alg)
        
        if any(v is None for v in self.board.values()):            
            raise InvalidBoardFormat("Board contains unintialized values.") 
           
        if len(missing_keys) > 0:
            err:str = ""
            for mk in missing_keys:
                err = f"{mk}, "
                
                raise InvalidBoardFormat(f"Board is missing keys: {err}") 
        return True
    
    def _parse_fen(self, fen:str):
        validate_fen(fen)
        self.validate_board()
        
        for val in self.board.values():
            val.kill()
        
        #Board only cares about piece placement
        pieces = fen.split(" ")[0] 
        rows = pieces.split("/")

        def set_val(row:int, col:int, val:ImageTk.PhotoImage):
            key:str | None = get_algebraic(row, col)
            if key:
                if self.board.get(key) is not None:
                    self.board[key].set_image(val)
                    
        count:int = 0
            
        for i, row in enumerate(rows):
            col_idx:int = 0
            
            for col in row:
                if col_idx > 7:
                    raise Exception("Column mis-count, too high!") # pylint: disable=broad-exception-raised
                
                if col.isdigit():
                    for _ in range(int(col)):
                        col_idx += 1
                else:                    
                    set_val(i, col_idx, self.image_map[col])
                    col_idx += 1
            
            if col_idx != 8:
                raise Exception(f"Column mis-count, {col_idx} too low!") # pylint: disable=broad-exception-raised
            count += col_idx
            
        if count != 64:
            raise Exception("Missing maps") # pylint: disable=broad-exception-raised    
    
    def _dispatch(self, event:Event, data: dict[str, Any] | None = None): 
        if data is None:
            data = {}

        print("dispatch")    
        
    def _initialize(self):
        """
        Initializes self.board_map and creates a background image

        Returns:
           ImageTk.PhotoImage: background image
           
        Raises:
            Exception if self.board_map was initialized with 64 values
        """
        
        dim:int = self.square_size * 8
        background:Image.Image = Image.new('RGBA', (dim, dim))
        draw:ImageDraw.ImageDraw = ImageDraw.Draw(background)
        self.board = {}

        for row in range(8):
            for col in range(8):
                key:str | None = get_algebraic(row, col)
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                top_x:int = col * self.square_size
                top_y:int = row * self.square_size
                bot_x: int = top_x + self.square_size
                bot_y: int = top_y + self.square_size
                draw.rectangle([(top_x, top_y),(bot_x, bot_y)], color)
                
                if key:
                    self.board[key] = SquareInfo(top_x + 2, top_y + 2, self.square_size-4, self.square_size-4)
                    
        if len(self.board) != 64:
            raise Exception("Failed to Initialize board")
        self.background_img = ImageTk.PhotoImage(background)
        self.display_image(self.background_img)

    def display_image(self, img: ImageTk.PhotoImage, x_pos:int=0, y_pos:int=0):
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=img)
        self.root.update_idletasks()
        self.root.update()   
        

# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Chess")
#     board_display:BoardDisplay = BoardDisplay(root, 768, 1024, IMAGE_MAP)

#     board_display.draw(STARTING_FEN)

#     root.mainloop() 

    
# Highlight selected square
# if self.selected_square is not None and (row, col) == self.selected_square:
#     pygame.draw.rect(screen, SELECTED_SQUARE_COLOR, (col *
#                         SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

# # Draw pieces
# piece = str(self.board.piece_at(chess.square(col, 7 - row)))
# if piece != "None":
#     image = PIECE_IMAGES[piece]
#     screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))