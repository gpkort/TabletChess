import tkinter as tk
from PIL import Image

from Display import BoardDisplay
from Input import TkButtonInputHandler

ENGINE:str = r"C:\temp\stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 1024

# engine = chess.engine.SimpleEngine.popen_uci(ENGINE)

def main():
    root = tk.Tk()
    root.title("Chess")
    board_display:BoardDisplay = BoardDisplay(root, SCREEN_WIDTH, SCREEN_HEIGHT)
    buttons:TkButtonInputHandler = TkButtonInputHandler(root)
    

    root.mainloop() 

    # pygame.init()
    # screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # pygame.display.set_caption("Chess Game with Stockfish")

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
