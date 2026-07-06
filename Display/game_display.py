import tkinter as tk
from typing import Any, Tuple, Callable
from PIL import Image, ImageTk
import chess
from chess import Board
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
    def __init__(self,
                 name:str,
                 x:int,
                 y:int,
                 button:tk.Button,
                 win_id:int,
                 callback: Callable[[str], None],
                 *,
                 img_id:int = -1,
                 image:ImageTk.PhotoImage | None = None,
                 selected:bool = False):
        
        self._x:int = x
        self._y:int = y
        self._image:ImageTk.PhotoImage | None = image
        self._image_id:int = img_id
        self._selected:bool = selected
        self.button:tk.Button = button
        self.name:str = name
        self.callback = callback
        
        self._window_id = win_id
        self.button.bind("<Button-1>", func=self.click_event)

    def click_event(self, event:tk.Event):  # pylint: disable=unused-argument
        self.callback(self.name)

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
    def image_id(self) -> int:
        return self._image_id   #type: ignore 
    @image_id.setter
    def image_id(self, value:int):
        self._id = value
    @property
    def selected(self) -> bool:
        return self.selected
    @selected.setter
    def selected(self, value):
        self.selected = value  
           
    def set_image(self, img:ImageTk.PhotoImage, id:int=-1):
        self._image_id = id
        self._image = img
    
    def place(self, id:int, img:ImageTk.PhotoImage):
        self._image_id = id
        self._image = img
        
    def move(self)->Tuple[int, ImageTk.PhotoImage|None]:
        img = self._image
        id = self._id
        self._image_id = -1
        self._image = None
        return (id, img) # type: ignore
    
    def kill(self):
        self._id = -1
        self._image = None
    
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

class BoardDisplay(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, root: tk.Tk,
                 width: int,
                 height: int,
                 pieces_map:dict[str, str], *,                 
                 initial_setup:str | None = None,
                 rotation: int = 0):

        super().__init__()
        self.width = width
        self.height = height
        self.rotation = 0
        self.square_size:int = self.width // BOARD_SIZE
                
        self.root: tk.Tk = root        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.width) #make it square
        self.canvas.pack(fill="both", expand=True)
        
        self.board:Board = Board()
        
        self.board_display:dict[str, SquareInfo] = {}
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

    def dispatchButton(self, name:str):        
        super()._dispatch(DisplayEvent.SQUARE_CLICK, {"piece":name})
        print(f"Name: {name}")
        piece:chess.Piece | None = self.board.piece_at(chess.parse_square(name))
        if piece:
            print(piece.symbol)

    def new_game(self):
        self.board.reset()
        for key, val in self.board_display.items():
            val.kill()
            piece:chess.Piece | None = self.board.piece_at(chess.parse_square(key))
            if piece:
                print(f"{key} = {piece.symbol()}, id = {val.image_id}")
                sym:str = piece.symbol()                
                self.board_display[key].set_image(self.image_map[sym])      
            
        


        self.draw()
        
    def draw(self):
        #self._parse_fen(fen)

        for square in self.board_display.values():
            if square.image:
                square.button.config(image=square.image)
                        
    def validate_board(self):
        missing_keys:list[str] = []
        for l in range(97, 105):
            for i in range(1, 9):
                alg:str = chr(l) + str(i)
                if alg not in list(self.board_display.keys()):
                    missing_keys.append(alg)
        
        if any(v is None for v in self.board_display.values()):            
            raise InvalidBoardFormat("Board contains unintialized values.") 
           
        if len(missing_keys) > 0:
            err:str = ""
            for mk in missing_keys:
                err = f"{mk}, "
                
                raise InvalidBoardFormat(f"Board is missing keys: {err}") 
        return True
    
    def _parse_fen(self, fen:str):        
        validate_fen(fen)        
        for val in self.board_display.values():
            val.kill()
        
        #Board only cares about piece placement
        pieces = fen.split(" ")[0] 
        rows = pieces.split("/")

        def set_val(row:int, col:int, val:ImageTk.PhotoImage):
            key:str | None = get_algebraic(row, col)
            if key:
                if self.board_display.get(key) is not None:
                    self.board_display[key].set_image(val)
                    
        count:int = 0
            
        for i, row in enumerate(rows):
            col_idx:int = 0
            
            for col in row:
                                
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
                top_x:int = file * self.square_size
                top_y:int = rank * self.square_size
                
                name:str = chess.square_name(chess.square(file, rank)) 
                print(f"{name} = ({top_x}, {top_y})")               
                button = tk.Button(self.canvas, 
                                   background=color,
                                   width=self.square_size, 
                                   height=self.square_size)
                window_id:int = self.canvas.create_window(top_x, top_y, anchor="nw", window=button)
                self.board_display[name] = SquareInfo(name, top_x, top_y, button, window_id, self.dispatchButton)
        

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
# piece = str(self.board_display.piece_at(chess.square(col, 7 - row)))
# if piece != "None":
#     image = PIECE_IMAGES[piece]
#     screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))