import tkinter as tk
from tkinter import ttk
from .handler import Event, EventDispatcher


class TkButtonInputHandler(EventDispatcher):
    def __init__(self, root: tk.Tk):
        super().__init__()
        self.root = root

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        self.game_combo = ttk.Combobox(self.frame, state="disabled")
        self.game_combo.bind("<<ComboboxSelected>>", self.puzzle_select)

        self.puzzle_combo = ttk.Combobox(self.frame, state="disabled")
        self.puzzle_combo.bind("<<ComboboxSelected>>", self.puzzle_select)

        self.layout_interface()

    def layout_interface(self):
        game_button = tk.Button(self.frame, text="New Game", command=lambda: self._dispatch(Event.NEW_GAME))
        game_button.grid(row=1, column=1)
        load_game_btn = tk.Button(self.frame, text="Load Game", command=lambda: self._dispatch(Event.LOAD_GAME))
        load_game_btn.grid(row=1, column=2)
        self.game_combo.grid(row=1, column=3)

        puzzle_button = tk.Button(self.frame, text="New Puzzle", command=lambda: self._dispatch(Event.NEW_PUZZLE))
        puzzle_button.grid(row=2, column=1)
        load_puzzle_button = tk.Button(self.frame, text="Load Puzzle", command=lambda: self._dispatch(Event.LOAD_PUZZLE))
        load_puzzle_button.grid(row=2, column=2)
        self.puzzle_combo.grid(row=2, column=3)

        quit_button = tk.Button(self.frame, text="Quit Current", command=lambda: self._dispatch(Event.QUIT_CURRENT))
        quit_button.grid(row=3, column=1)
        

    def puzzle_select(self, event):
        self._dispatch(Event.PUZZLE_SELECT, {"puzzle":event.widget.get()})

    def enable_puzzles(self, enable:bool):
        self.puzzle_combo.config(state=("readonly" if enable else "disabled"))

    def set_puzzles(self, puzzles:list[str], enable:bool=True):
        self.puzzle_combo.set(puzzles)
        self.enable_puzzles(enable)
        
