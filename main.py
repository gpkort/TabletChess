from GameManager import IMAGE_MAP, ChessManager

ENGINE:str = r"stockfish-windows-x86-64-avx2.exe"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600
# SCREEN_WIDTH = 1024
# SCREEN_HEIGHT = 768

       
cm:ChessManager = ChessManager(SCREEN_WIDTH, SCREEN_HEIGHT, ENGINE, 480, IMAGE_MAP)

def main():
    global cm
    cm.start()

    

if __name__ == "__main__":
    main()
