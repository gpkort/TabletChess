import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from enum import Enum
from typing import Any

class Event(Enum):
    NEW = 1

SCREEN_WIDTH = SCREEN_HEIGHT = 512
BOARD_SIZE = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECTED_SQUARE_COLOR = (255, 255, 0)

IMAGE_MAP = {
        "r": "b_rook.png",
        "n": "b_knight.png",
        "b": "b_bishop.png",
        "q": "b_queen.png",
        "k": "b_king.png",
        "p": "b_pawn.png",
        "R": "w_rook.png",
        "N": "w_knight.png",
        "B": "w_bishop.png",
        "Q": "w_queen.png",
        "K": "w_king.png",
        "P": "w_pawn.png",
    }

class BoardDisplay:
    """Tkinter display for chess game """
    
    def __init__(self, root: tk.Tk, width: int, height: int, rotation: int = 0):
        self.width = width
        self.height = height
        self.rotation = 0
        self.square_size:int = self.width // 8
                
        self.root = root        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.width) #make it square
        self.canvas.pack()
        self.imagesprite = None  # Keep reference to PhotoImage to prevent garbage collection

        self.board_image:Image.Image = self._create_board()
        self.display_image(self.board_image)
        self._create_buttons()

    def _create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        backward_button = tk.Button(button_frame, text="New", command=lambda: self._dispatch(Event.NEW))
        backward_button.grid(row=1, column=1)

    def _dispatch(self, event:Event, data: dict[str, Any] | None = None): 
        if data is None:
            data = {}

        print("dispatch")

    def _create_board(self) -> Image.Image:
        dim:int = self.square_size * 8
        background:Image.Image = Image.new('RGB', (dim, dim))
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

# Highlight selected square
# if self.selected_square is not None and (row, col) == self.selected_square:
#     pygame.draw.rect(screen, SELECTED_SQUARE_COLOR, (col *
#                         SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

# # Draw pieces
# piece = str(self.board.piece_at(chess.square(col, 7 - row)))
# if piece != "None":
#     image = PIECE_IMAGES[piece]
#     screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))