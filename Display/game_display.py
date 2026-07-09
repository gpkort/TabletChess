import tkinter as tk
from typing import Tuple
from PIL import ImageTk
import chess
from chess import Board, engine

from .square import SquareInfo
from .utility import load_pieces, create_transparent_image

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

class BoardDisplay():
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"
    WINDOW_CLOSE:str = "WM_DELETE_WINDOW"

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
        self.canvas.bind(self.TKINTER_LEFT_CLICK, self.left_mouse_click)
        self.root.protocol(self.WINDOW_CLOSE, self.on_closing)

        self.engine:engine.SimpleEngine = chess_engine
        self.engine.configure({"Skill Level": engine_skill_level})
        self.limit = engine.Limit(time=0.5)
        self.board:Board = Board()
        self.selected_square:chess.Square|None = None
        self.previous_square:chess.Square|None = None
        self.target_square:chess.Square|None = None
        self.legal_squares:list[chess.Square] = []

        self.board_display:dict[chess.Square, SquareInfo] = {}
        self.image_map:dict[str, ImageTk.PhotoImage] = load_pieces(pieces_map, self.square_size)
        self._initialize()

    def __del__(self):
        try:
            self.engine.quit()
        except engine.EngineTerminatedError as e:
            print(e)

    def on_closing(self):
        """
        Callback from close root frame
        """
        self.engine.close()
        self.root.destroy()

    def left_mouse_click(self, event:tk.Event):
        """
        user makes left click

        Args:
            event (tk.Event): event containing x, y coordinates
        """
        square:chess.Square | None = self.get_square(event.x, event.y)
        if square is None:
            return

        self.handle_square_selection(square)

    def new_game(self):
        """
        Start a new game
        """
        self.board.reset()
        self.update_board_display()        

    def handle_square_selection(self, square:chess.Square):
        """
        Either select a piece or move a piece if it's your turn and you clicked a 
        legal square

        Args:
            square (chess.Square): square that user clicked on.
        """
        if self.board.is_game_over() or self.board.turn != self.player_color:
            return

        if self.selected_square is None:
            piece:chess.Piece | None = self.board.piece_at(square)
            if piece is None or piece.color != self.board.turn:
                return
            self.legal_squares = self.get_legal_squares(square)
            self.selected_square = square
            self.previous_square = None
            self.target_square = None
        else:
            if self.selected_square == square:
                self.selected_square = None
                self.previous_square = None
                self.target_square = None
            else:
                piece:chess.Piece | None = self.board.piece_at(self.selected_square)
                if piece is None or piece.color != self.board.turn:
                    return
                if square in self.legal_squares:
                    self.board.push(chess.Move(self.selected_square, square))
                    pr:engine.PlayResult = self.engine.play(self.board, self.limit)
                    if pr.move:
                        self.board.push(pr.move)
                        self.previous_square = pr.move.from_square
                        self.target_square = pr.move.to_square
                    self.selected_square = None
                    self.legal_squares.clear()
        self.update_board_display()

    def update_board_display(self):
        """
        Iterates through squares and updates visual
        representation
        """
        for key, val in self.board_display.items():
            val.clear()

            piece:chess.Piece | None = self.board.piece_at(key)
            if piece:
                sym:str = piece.symbol()
                val.set_image(self.image_map[sym], True)

        if self.selected_square:
            self.board_display[self.selected_square].selected = True
        if self.previous_square:
            self.board_display[self.previous_square].show_move = True
        if self.target_square:
            self.board_display[self.target_square].show_move = True
        for legal in self.legal_squares:
            self.board_display[legal].legal = True

        self.update_root_display()

    def get_legal_squares(self, square:chess.Square)->list[chess.Square]:
        """
            return squares that can be leagally moved to
        Args:
            square (chess.Square): starting square
        """
        return [m.to_square for m in self.board.legal_moves if m.from_square == square]

    def get_square(self, x:int, y:int)->chess.Square|None:
        """
        Gets the square whre mouse click occured

        Args:
            x (int): x value of mouse click
            y (int): y value of mouse click

        Returns:
            chess.Square|None: The square or None 
        """
        for k, val in self.board_display.items():
            if val.x <= x <= val.x + self.square_size and val.y <= y <= val.y + self.square_size:
                return k

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
                self.board_display[square] = SquareInfo(self.canvas, name, x0, y0, 
                                                      self.square_size, 
                                                      create_transparent_image(self.square_size))


    def update_root_display(self):
        """
        call update for main loop
        """
        self.root.update_idletasks()
        self.root.update()

# import tkinter as tk

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