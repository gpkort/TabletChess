from typing import Tuple


from GameManager import STARTING_FEN, IMAGE_MAP

TEST:str = "rnbqkbnr/pp1ppppp/2p5/8/8/3P4/PPP1PPPP/RNBQKBNR w KQkq - 0 1"


class ClassA:
    def __init__(self, name:str="", age:int=0):
        self.name:str = name
        self.age:int = age
        
class ClassB:
    def __init__(self, id:int, ca:ClassA|None) :
        self.id = id
        self.ca:ClassA|None = ca
        
    def kill(self)-> ClassA|None:
        ca = self.ca
        self.ca = None
        return ca

def parse_fen(fen:str, board_map:dict[str, str]) :
    #Board only cares about piece placement
    pieces = fen.split(" ")[0] 
    rows = pieces.split("/")
    
    def set_val(row:int, col:int, val:str):
        key:str | None = get_algebraic(row, col)
        if key:
            if board_map.get(key) is not None:
                board_map[key] = val    
    count:int = 0
        
    for i, row in enumerate(rows):
        col_idx:int = 0
        
        for col in row:
            if col_idx > 7:
                raise Exception("Column mis-count, too high!") # pylint: disable=broad-exception-raised
            
            if col.isdigit():
                for _ in range(int(col)):
                    set_val(i, col_idx, "MS")
                    col_idx += 1
            else:
                set_val(i, col_idx, col)
                col_idx += 1
        
        if col_idx != 8:
            raise Exception(f"Column mis-count, {col_idx} too low!") # pylint: disable=broad-exception-raised
        count += col_idx
        
    if count != 64:
        raise Exception("Missing maps") # pylint: disable=broad-exception-raised    
    
   
def get_board(default:str="NONE") -> dict[str, str]:
    map:dict[str, str] = {}
    
    for idx in range(8):
        for jdx in range(8):
            key: str | None = get_algebraic(jdx, idx)
            
            if key:
                map[key] = default
    return map
    
def get_algebraic(col:int, row:int)->str | None:
    if (0 <= row <= 7) and (0 <= col <= 7):
        return chr(97 + col) + str(row + 1)
    
def print_board(board:dict[str, str]):
    for r in range(8):
        rstr:str = ""
        for c in range(8):
            key = get_algebraic(r, c)
            if key:
                rstr += f"{key}:{board[key]}, "
        rstr = rstr[:-2]
        print(rstr)

if __name__ == "__main__":
    print("start")
    
    # for l in range(97, 105):
    #     for i in range(1, 9):
    #         alg:str = chr(l) + str(i)
    #         print(alg)
    
    for row in range(8):
        for col in range(8):
            key:str | None = get_algebraic(col, row)
            print(key)
    
    
           