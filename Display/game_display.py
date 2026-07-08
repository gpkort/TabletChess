import tkinter as tk
from typing import Any, Tuple
from PIL import ImageTk
import chess
from chess import Board, engine

from Display import SquareInfo, load_pieces
from Input import Event as DisplayEvent, EventDispatcher

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

class BoardDisplay(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, root: tk.Tk,
                 width:int,
                 height:int,
                 board_size: int,
                 pieces_map:dict[str, str],
                 chess_engine: engine.SimpleEngine,
                 *,
                 is_single_player:bool = True,
                 single_player_is_white:bool = True,
                 engine_skill_level:int = 0):

        super().__init__()
        
        self.square_size:int = board_size // BOARD_SIZE
        self.is_single_player:bool = is_single_player
        self.player_color:chess.Color = chess.WHITE if single_player_is_white else chess.BLACK

        self.root: tk.Tk = root
        self.canvas = tk.Canvas(self.root, width=width, height=height) #make it square
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.dispatchButton)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.engine:engine.SimpleEngine = chess_engine
        self.engine.configure({"Skill Level": engine_skill_level})
        self.limit = engine.Limit(time=0.5)
        self.board:Board = Board()
        self.selected_square:chess.Square|None = None

        self.board_display:dict[chess.Square, SquareInfo] = {}
        self.image_map:dict[str, ImageTk.PhotoImage] = load_pieces(pieces_map) 
        self._initialize()

    def __del__(self):
        try:
            self.engine.quit()
        except engine.EngineTerminatedError as e:
            print(e)

    def on_closing(self):
        self.engine.close()
        self.root.destroy()

    def dispatchButton(self, event:tk.Event):
        square:chess.Square | None = self.get_square(event.x, event.y)
        if square is None:
            return

        self.handle_square_selection(square)

    def new_game(self):
        self.board.reset()
        self.update_board_display()        
    
    def handle_square_selection(self, square:chess.Square):
        if self.board.is_game_over() or self.board.turn != self.player_color:
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
                        self.move_piece(self.selected_square, square, True)
                        self.update_board_display()
                        break
 
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

    def move_piece(self, from_square:chess.Square, to_square:chess.Square, engine_move:bool = False)->bool:
        move = chess.Move(from_square, to_square)
        if move in self.board.legal_moves:
            self.board.push(move)
            if engine_move:
                pr:engine.PlayResult = self.engine.play(self.board, self.limit)
                if pr.move:
                    self.board.push(pr.move)
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
        self.update_root_display()

    def update_root_display(self):
        self.root.update_idletasks()
        self.root.update()  

import tkinter as tk

# Initialize the main application window
# root = tk.Tk()
# root.title("Multiline Textbox on Canvas")
# root.geometry("500x400")

# # 1. Create the Canvas widget
# canvas = tk.Canvas(root, width=500, height=400, bg="#e0e0e0")
# canvas.pack(fill="both", expand=True)

# # Draw a background shape on the canvas to show depth
# canvas.create_rectangle(50, 50, 450, 350, fill="#ffffff", outline="#b0b0b0")

# # 2. Create the multiline Text widget
# # Note: 'height' is measured in lines of text, and 'width' is in characters
# text_box = tk.Text(canvas, width=40, height=8, wrap="word", bd=2, relief="groove")

# # (Optional) Pre-fill the textbox with some default text
# text_box.insert("1.0", "Type your multiline content here...\nLine 2\nLine 3") #

# # 3. Embed the Text widget into the Canvas
# # The coordinates (250, 200) dictate the anchor point on the canvas
# canvas.create_window(250, 200, window=text_box, anchor="center") #

# # Run the Tkinter application loop
# root.mainloop() #