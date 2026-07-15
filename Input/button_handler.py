import tkinter as tk
from tkinter import ttk
from .handler import Event, EventDispatcher


class TkButtonInputHandler(EventDispatcher):
    def __init__(self, root: tk.Tk):
        super().__init__()
        self.root = root

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        self.combo = ttk.Combobox(self.frame, state="disabled")
        self.combo.bind("<<ComboboxSelected>>", self.puzzle_select)

        self.layout_interface()

    def layout_interface(self):
        
        
        new_button = tk.Button(self.frame, text="New", command=lambda: self._dispatch(Event.NEW))
        new_button.grid(row=1, column=1)

        puzzle_button = tk.Button(self.frame, text="Puzzles", command=lambda: self._dispatch(Event.PUZZLES))
        puzzle_button.grid(row=1, column=2)
        self.combo.grid(row=1, column=3)

    def puzzle_select(self, event):
        self._dispatch(Event.PUZZLE_SELECT, {"puzzle":event.widget.get()})

    def enable_puzzles(self, enable:bool):
        self.combo.config(state=("readonly" if enable else "disabled"))

    def set_puzzles(self, puzzles:list[str], enable:bool=True):
        self.combo.set(puzzles)
        self.enable_puzzles(enable)
        
