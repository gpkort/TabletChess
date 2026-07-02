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

@dataclass
class PieceInfo :
    current_agebraic: str = ""
    tag:str = ""
    img:ImageTk.PhotoImage | None = None


def validate_fen(fen:str):
    if not all(c in ALLOWABLE_CHARS for c in fen):
        raise InvalidFenFormat("Contains unallowed characters")
    if fen.split(" ")[0] is None:
        raise InvalidFenFormat("Does not contain row information")
    
    rows = (fen.split(" ")[0]).split("/")
    if len(rows) != 8:
        raise InvalidFenFormat(f"Does not information for all 8 rows {fen.split(" ")[0]}")
    
    for row in rows:
        if not any(c not in ROW_CHARS for c in fen):
            raise InvalidFenFormat(f"row: {row} contains invalid chars for piece placement")
        row_len = 0
        for p in row:
            if p.isdigit():
                row_len += int(p)
            else:
                row_len += 1
        if row_len != 8:
            raise InvalidFenFormat(f"Does row does not contain all information for 8 squares {row}")

# https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation#
def parse_fen(fen:str) -> list[list[str]]: 
    validate_fen(fen)
    board:list[list[str]] = [[] for _ in range(BOARD_SIZE)]

    #Board only cares about piece placement
    pieces = fen.split(" ")[0] 

    rows = pieces.split("/")
    if len(rows) != 8:
        raise Exception("Invalid FEN fomat")
    
    for i, row in enumerate(rows):
        for p in row:
            if p.isdigit():
                board[i].extend([" " for _ in range(int(p) + 1)])
            else:
                board[i].append(p) 

    return board

def get_row_col(alg:str) -> Tuple[int, int] | None:
    lt:list[str] = [chr(i) for i in range(96, 105)]
    nu:list[str] = [str(i) for i in range(1, 9)]
    if len(alg) == 2 and (alg[0] in lt) and (alg[1] in nu):
        return (int(alg[1]), ord(alg[0])-96)
    
def get_algebraic(col:int, row:int)->str | None:
    if (1 <= row <= 8) and (1 <= col <= 8):
        return chr(96 + col) + str(row)

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
        self.canvas.pack()
        self.background_img:ImageTk.PhotoImage | None = None  # Keep reference to PhotoImage to prevent garbage collection

        self.board:list[list[PieceInfo]] = [[ PieceInfo() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.image_map:dict[str, ImageTk.PhotoImage] = self._load_pieces(pieces_map) 
        self.board_image:ImageTk.PhotoImage = self._create_board_image()
        self.display_image(self.board_image)

    def _load_pieces(self, pieces_map:dict[str, str]) -> dict[str, ImageTk.PhotoImage]:
        """stores images into map

        This method takes two integer inputs, computes their sum,
        and returns the result.

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
        board = parse_fen(fen)
        found_B, found_R, found_N = False, False, False
        found_b, found_r, found_n = False, False, False

        for i, row in enumerate(board):
            for j, col in enumerate(row):  
                pi:PieceInfo = PieceInfo()
                
                ac:str | None = get_algebraic(j+1, i+1)
                img:ImageTk.PhotoImage | None = self.image_map.get(col, None)

                if ac and img:
                    pi.current_agebraic = ac
                    pi.tag = col + "_" + ac
                    pi.img = img

                    x = j*self.square_size + 2, 
                    y = i*self.square_size + 2
                    self.canvas.create_image(x, y, anchor="nw", image=pi.img, tags=pi.tag)
                    self.canvas.tag_bind(pi.tag, "<Button-1>", self._tkinter_click)

                    self.board[i][j] = pi

    def _tkinter_click(self, event):
        print(event)
    
    def _dispatch(self, event:Event, data: dict[str, Any] | None = None): 
        if data is None:
            data = {}

        print("dispatch")

    def _create_board_image(self) -> ImageTk.PhotoImage:
        dim:int = self.square_size * 8
        background:Image.Image = Image.new('RGBA', (dim, dim))
        draw:ImageDraw.ImageDraw = ImageDraw.Draw(background)

        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                top_x:int = col * self.square_size
                top_y:int = row * self.square_size
                bot_x: int = top_x + + self.square_size
                bot_y: int = top_y + + self.square_size

                draw.rectangle([(top_x, top_y),(bot_x, bot_y)], color)
                
        return ImageTk.PhotoImage(background)

    def display_image(self, img: ImageTk.PhotoImage, x_pos:int=0, y_pos:int=0):
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=img)
        self.root.update_idletasks()
        self.root.update()

    
        ...

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