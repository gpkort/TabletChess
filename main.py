import tkinter as tk
# from PIL import Image
from typing import Any

import chess
from chess import Board

from Display import BoardDisplay
from Input import TkButtonInputHandler, Event, EventHandler
from GameManager import STARTING_FEN, IMAGE_MAP

ENGINE:str = r"C:\temp\stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
# SCREEN_WIDTH = 1024
# SCREEN_HEIGHT = 768

       

root = tk.Tk()
root.title("Chess")
board_display:BoardDisplay = BoardDisplay(root, SCREEN_WIDTH, SCREEN_HEIGHT, IMAGE_MAP)
buttons:TkButtonInputHandler = TkButtonInputHandler(root)

# engine = chess.engine.SimpleEngine.popen_uci(ENGINE)

 

def new_game(event:Event, data:dict[str, Any]):
    board_display.draw(STARTING_FEN)

def main():       
    buttons.register_handler(EventHandler(Event.NEW, new_game))   

    root.mainloop()
        
    # # Replace with your engine path
    # # engine_path = "D:/project_learn/Python/stockfish-windows-x86-64-avx2.exe"
    # # game = Game(engine_path)
    # ENGINE:str = r"C:\temp\stockfish-windows-x86-64-avx2.exe"
    # # game = Game(ENGINE)

    # running = True
    # while running:
    #     game.make_ai_move()  # AI's turn
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #         elif event.type == pygame.MOUSEBUTTONDOWN:
    #             game.handle_mouse_click(pygame.mouse.get_pos())

    #     game.update_game_state()
    #     game.draw(screen)
    #     pygame.display.flip()

    # game.engine.quit()
    # pygame.quit()


if __name__ == "__main__":
    main()
