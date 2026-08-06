from dataclasses import dataclass, field
from typing import Any, Tuple
from enum import Enum

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import ImageTk
import chess

from Input import EventDispatcher, Event
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

class SaveResult(Enum):
    SAVE = 0
    NO_SAVE = 1
    CANCEL = 2
    UNKNOWN = 99

@dataclass
class DisplayInfo:
    selected_square:chess.Square|None = None
    previous_square:chess.Square|None = None
    target_square:chess.Square|None = None
    legal_squares:list[chess.Square] = field(default_factory=list)
    piece_location:dict[chess.Square, str] = field(default_factory=dict)

class BoardDisplay(EventDispatcher):
    """Tkinter display for chess game """
    TKINTER_LEFT_CLICK:str = "<Button-1>"

    def __init__(self, root: tk.Tk,
                 width:int,
                 height:int,
                 board_size: int,
                 pieces_map:dict[str, str]):
                

        super().__init__()
        
        self.square_size:int = board_size // BOARD_SIZE
        

        self._root: tk.Tk = root
        self._canvas = tk.Canvas(self._root, width=width, height=height)
        self._text_box = tk.Text(self._canvas, width=58, height=8, wrap="word", bd=2, relief="groove")
        self._text_box.config(state=tk.DISABLED)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind(self.TKINTER_LEFT_CLICK, self._left_mouse_click)

        self._board_display:dict[chess.Square, SquareInfo] = {}
        self._image_map:dict[str, ImageTk.PhotoImage] = load_pieces(pieces_map, self.square_size)
        self._initialize(board_size, width)

    def _left_mouse_click(self, event:tk.Event):
        """
        user makes left click

        Args:
            event (tk.Event): event containing x, y coordinates
        """
        square:chess.Square | None = self.get_square(event.x, event.y)
        if square is not None:
            self._dispatch(Event.SQUARE_CLICK, {"square": square})

    def get_player_yes_no(self, title:str, text:str)->bool:
        return messagebox.askyesno(title, text)  

    def get_player_input(self, title:str, text:str)->str|None:
        return simpledialog.askstring(title, text)

    def save_activity_prompt(self)->Tuple[SaveResult, str]:
        result:SaveResult = SaveResult.UNKNOWN
        activity_name:str  = ""

        res:bool|None = messagebox.askyesnocancel("Save, Don't save, Cancel", "Do you want to quit game and Save, quit and not Save, or cancel")
        if res is None:
            result = SaveResult.CANCEL
        else:
            result = SaveResult.SAVE if res else SaveResult.NO_SAVE

        if res == SaveResult.SAVE:
            tname:str | None = simpledialog.askstring("Activity Name to Save", "Blank will not be save!")
            activity_name = tname if tname is not None else ""
            result = SaveResult.SAVE if tname is not None else SaveResult.NO_SAVE            

        return (result, activity_name)

    def set_player_alert(self, title:str, text:str, icon:Any|None=None):

        if icon:
            messagebox.showinfo(title, text, icon=icon)
        else:
             messagebox.showinfo(title, text)
  
    def update_board_display(self, display_info:DisplayInfo):
        """
        Iterates through squares and updates visual
        representation
        """
        for key, val in self._board_display.items():
            val.clear()

        for square, piece_str in display_info.piece_location.items():
            self._board_display[square].set_image(self._image_map[piece_str], True)

        if display_info.selected_square:
            self._board_display[display_info.selected_square].selected = True
        if display_info.previous_square:
            self._board_display[display_info.previous_square].show_move = True
        if display_info.target_square:
            self._board_display[display_info.target_square].show_move = True
        for legal in display_info.legal_squares:
            self._board_display[legal].legal = True

        self.update_root_display()
    
    def get_square(self, x:int, y:int)->chess.Square|None:
        """
        Gets the square whre mouse click occured

        Args:
            x (int): x value of mouse click
            y (int): y value of mouse click

        Returns:
            chess.Square|None: The square or None 
        """
        for k, val in self._board_display.items():
            if val.x <= x <= val.x + self.square_size and val.y <= y <= val.y + self.square_size:
                return k

    def set_text(self, text:str):
        self._text_box.config(state=tk.NORMAL)
        self._text_box.delete("1.0", tk.END)
        self._text_box.insert("1.0", text)
        self._text_box.config(state=tk.DISABLED)

    def append_text(self, text:str):
        self._text_box.config(state=tk.NORMAL)
        current_txt:str = self._text_box.get("1.0", tk.END)
        self._text_box.delete("1.0", tk.END)
        self._text_box.insert("1.0", (current_txt+"\n"+text))
        self._text_box.config(state=tk.DISABLED)

    def _initialize(self, board_size:int, width:int):
        """
        Initializes self._board_display_map and creates a background image

        Returns:
           ImageTk.PhotoImage: background image
           
        Raises:
            Exception if self._board_display was initialized with 64 values
        """
        
        self._canvas.create_window(5, board_size + 10, window=self._text_box, anchor="nw") 
        self._board_display = {}
        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                color:str = LIGHT_SQUARE_COLOR if (rank + file) % 2 == 0 else DARK_SQUARE_COLOR
                x0:int = file * self.square_size
                y0:int = rank * self.square_size
                x1:int = x0 + self.square_size
                y1:int = y0 + self.square_size

                square:chess.Square = chess.square(file, 7-rank)
                name:str = chess.square_name(square)
                
                self._canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                self._board_display[square] = SquareInfo(self._canvas, name, x0, y0,
                                                      self.square_size,
                                                      create_transparent_image(self.square_size))

    def update_root_display(self):
        """
        call update for main loop
        """
        self._root.update_idletasks()
        self._root.update()

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