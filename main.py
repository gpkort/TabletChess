from os import path

from GameManager import (IMAGE_MAP, 
                         ChessManager,
                         PuzzleEnginePickel,
                         GamePersisterDF, 
                         DEFAULT_PERSIST_DF)


# from GameManager import PuzzleEnginePickel, Puzzle, Theme

PICKLE_DIR = "C:\\Users\\gkorthuis\\source\\MyChess"
ENGINE:str = "stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
# SCREEN_WIDTH = 1024
# SCREEN_HEIGHT = 768

pe_pk:PuzzleEnginePickel = PuzzleEnginePickel(path.join(PICKLE_DIR, "puzzle_pk"), path.join(PICKLE_DIR,"theme_pk"))       
cm:ChessManager = ChessManager(SCREEN_WIDTH, SCREEN_HEIGHT, 480, ENGINE, IMAGE_MAP, pe_pk, GamePersisterDF(game_df=None) )

def main():
    global cm
    cm.start()

    

if __name__ == "__main__":
    main()
