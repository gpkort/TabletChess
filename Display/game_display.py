import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from enum import Enum
from typing import Any, Tuple
import numpy as np

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

IMAGE_MAP:dict[str, str] = {
        "r": r"assets\imgs\b_rook.png",
        "n": r"assets\imgs\b_knight.png",
        "b": r"assets\imgs\b_bishop.png",
        "q": r"assets\imgs\b_queen.png",
        "k": r"assets\imgs\b_king.png",
        "p": r"assets\imgs\b_pawn.png",
        "R": r"assets\imgs\w_rook.png",
        "N": r"assets\imgs\w_knight.png",
        "B": r"assets\imgs\w_bishop.png",
        "Q": r"assets\imgs\w_queen.png",
        "K": r"assets\imgs\w_king.png",
        "P": r"assets\imgs\w_pawn.png",
    }

STARTING_FEN:str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class InvalidFenFormat(Exception):
    """Raised when a string containing Forsyth–Edwards Notation is invalid"""

class Board:
    ALLOWABLE_CHARS:str = "rnbqkpRNBQKP012345678w /-"
    ROW_CHARS:str = "rnbqkpRNBQKP012345678"
    def __init__(self, inital:str | None = None):
        self._board:list[list[str]] = [[" " for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        if inital:
            self.parse_fen(inital)


    @property
    def board_array(self) -> list[list[str]]:
        return self._board.copy()

    # https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation#
    def parse_fen(self, fen:str): 
        self.validate_fen(fen)
        self._board = [[] for _ in range(BOARD_SIZE)]

        #Board only cares about piece placement
        pieces = fen.split(" ")[0] 

        rows = pieces.split("/")
        if len(rows) != 8:
            raise Exception("Invalid FEN fomat")
        
        for i, row in enumerate(rows):
            for p in row:
                if p.isdigit():
                    self._board[i].extend([" " for _ in range(int(p) + 1)])
                else:
                    self._board[i].append(p)        

    def validate_fen(self, fen:str):
        if not all(c in self.ALLOWABLE_CHARS for c in fen):
            raise InvalidFenFormat("Contains unallowed characters")
        if fen.split(" ")[0] is None:
            raise InvalidFenFormat("Does not contain row information")
        
        rows = (fen.split(" ")[0]).split("/")
        if len(rows) != 8:
            raise InvalidFenFormat(f"Does not information for all 8 rows {fen.split(" ")[0]}")
        
        for row in rows:
            if not any(c not in self.ROW_CHARS for c in fen):
                raise InvalidFenFormat(f"row: {row} contains invalid chars for piece placement")
            row_len = 0
            for p in row:
                if p.isdigit():
                    row_len += int(p)
                else:
                    row_len += 1
            if row_len != 8:
                raise InvalidFenFormat(f"Does row does not contain all information for 8 squares {row}")

    def __str__(self) -> str:
        ret = ""
        for row in self.board:
            ln:str = ""
            for sq in row:
                ln += sq + " "
            ret += ln[:-1] + "\n"

        return ret

class BoardDisplay:
    """Tkinter display for chess game """
    
    def __init__(self, root: tk.Tk, width: int, height: int, rotation: int = 0, pieces_map:dict[str, str] = IMAGE_MAP):
        self.width = width
        self.height = height
        self.rotation = 0
        self.square_size:int = self.width // 8
                
        self.root = root        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.width) #make it square
        self.canvas.pack()
        self.imagesprite = None  # Keep reference to PhotoImage to prevent garbage collection

        self.board:Board = Board()

        self.pieces_map:dict[str, Image.Image] = self.load_pieces(pieces_map) 
        self.board_image:Image.Image = self._create_board_image()
        self.display_image(self.board_image)
        self._create_buttons()

    def load_pieces(self, piece_map:dict[str, str]) -> dict[str, Image.Image]:
        images:dict[str, Image.Image] = {}

        for k,v in piece_map.items():
            image = Image.open(v)

            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image = image.resize((self.square_size, self.square_size))

            pixs = np.array(image)
            new_pixes = []
            r, g, b, a = pixs[:,:,0], pixs[:,:,1], pixs[:,:,2], pixs[:,:,3]
            white = (r==255) & (g== 55) & (b==225)
            pixs[..., 3] = np.where(white, 0, a)
            images[k] = Image.fromarray(pixs)

        return images

    def draw(self, fen:str):
        self.board.parse_fen(fen)
        board = self.board.board_array

        for i, row in enumerate(board):
            for j, col in enumerate(row):                
                img:Image.Image | None = self.pieces_map.get(col, None)

                if img:
                    pos = (j*self.square_size, i*self.square_size)
                    self.board_image.paste(img, pos, img)

        self.display_image(self.board_image)

    def _create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        backward_button = tk.Button(button_frame, text="New", command=lambda: self._dispatch(Event.NEW))
        backward_button.grid(row=1, column=1)

    def _dispatch(self, event:Event, data: dict[str, Any] | None = None): 
        if data is None:
            data = {}

        print("dispatch")

    def _create_board_image(self) -> Image.Image:
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
                
        return background

    def display_image(self, image: Image.Image, x_pos:int=0, y_pos:int=0):
        tk_img = ImageTk.PhotoImage(image)
        self.imagesprite = tk_img
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=tk_img)
        self.root.update_idletasks()
        self.root.update()

    def sleep(self):
        ...

    def cleanup(self):
        ...

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")
    board_display:BoardDisplay = BoardDisplay(root, 768, 1024)

    board_display.draw(STARTING_FEN)

    root.mainloop() 

    
# Highlight selected square
# if self.selected_square is not None and (row, col) == self.selected_square:
#     pygame.draw.rect(screen, SELECTED_SQUARE_COLOR, (col *
#                         SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

# # Draw pieces
# piece = str(self.board.piece_at(chess.square(col, 7 - row)))
# if piece != "None":
#     image = PIECE_IMAGES[piece]
#     screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))