import tkinter as tk
from .handler import Event, EventDispatcher


class TkButtonInputHandler(EventDispatcher):
    def __init__(self, root: tk.Tk):
        super().__init__()
        self.root = root
        self.create_buttons()

    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        backward_button = tk.Button(button_frame, text="New", command=lambda: self._dispatch(Event.NEW))
        backward_button.grid(row=1, column=1)