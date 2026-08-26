from enum import Enum
from dataclasses import dataclass, field

import tkinter as tk
from tkinter import ttk, scrolledtext
from .handler import Event, EventDispatcher

class ChessWidgetType(Enum):
    BUTTON = 1
    DROP_DOWN = 2

@dataclass
class ChessWidget:
    name:str
    widget_type:ChessWidgetType

class ChessUI(EventDispatcher):
    def __init__(self, width:int, height:int, chess_board_size:int, *, title:str="Chess"):
        super().__init__()

        self._root = tk.Tk()

        self._root.title(title)        
        self._root.geometry(f"{width}x{height}")

        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # self._main_frame:ttk.Frame = ttk.Frame(self._root, relief="groove")
        self._main_frame:ttk.Frame = ttk.Frame(self._root, padding=10)
        self._main_frame.pack(fill=tk.BOTH, expand=True)
        self._main_frame.rowconfigure(0, weight=1)
        self._main_frame.rowconfigure(1, weight=1)
        self._main_frame.rowconfigure(2, weight=1)
        self._main_frame.columnconfigure(0, weight=1)

        self._canvas:tk.Canvas = tk.Canvas(self._main_frame, 
                                           width=chess_board_size, height=chess_board_size, 
                                           bd=2, relief="groove")
        self._canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # self._canvas.pack(fill="both", expand=True)

        # self._text_box = scrolledtext.ScrolledText(self._main_frame, wrap=tk.WORD, width=40, height=40)
        # self._text_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        # # self._text_box.pack(fill="both", expand=True)
        # # text_area.config(state='disabled')

        self._widget_frame:ttk.LabelFrame = ttk.LabelFrame(self._main_frame, relief="groove", 
                                               width=480, height=40)
        self._widget_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        # self._widget_frame.pack(fill="both", expand=True)
        

    @property
    def canvas(self)->tk.Canvas:
        return self._canvas

    @property
    def widget_frame(self)->ttk.LabelFrame:
        return self._widget_frame

    def start(self)->None:
        self._root.mainloop()

    #region Private methods

    def _on_closing(self):
        self._root.destroy()
        self._dispatch(Event.QUIT)

    #endregion
