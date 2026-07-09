import tkinter as tk
from typing import Any

from chess import engine
from Display import BoardDisplay
from Input import TkButtonInputHandler, Event, EventHandler
from GameManager import IMAGE_MAP

ENGINE:str = r"stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
# SCREEN_WIDTH = 1024
# SCREEN_HEIGHT = 768

       

root = tk.Tk()
root.title("Chess")
board_display:BoardDisplay = BoardDisplay(root, SCREEN_WIDTH, SCREEN_HEIGHT, 480, IMAGE_MAP, 
                                          engine.SimpleEngine.popen_uci(ENGINE))
buttons:TkButtonInputHandler = TkButtonInputHandler(root)

def new_game(event:Event, data:dict[str, Any]):
    board_display.new_game()

def main():
    buttons.register_handler(EventHandler(Event.NEW, new_game))

    root.mainloop()
        
    

if __name__ == "__main__":
    main()
