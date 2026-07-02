from typing import Tuple

def get_row_col(alg:str) -> Tuple[int, int] | None:
    lt:list[str] = [chr(i) for i in range(96, 105)]
    nu:list[str] = [str(i) for i in range(1, 9)]
    if len(alg) == 2 and (alg[0] in lt) and (alg[1] in nu):
        return (int(alg[1]), ord(alg[0])-96)
    
def get_algebraic(col:int, row:int)->str | None:
    if (1 <= row <= 8) and (1 <= col <= 8):
        return chr(96 + col) + str(row)

if __name__ == "__main__":
    test: list[list[int]] = [[i for i in range(8)] for _ in range(8)]

    print(get_row_col("b7"))
    print(get_row_col("97"))
    print(get_row_col("p7"))
    print(get_row_col("d4"))

    print(get_algebraic(7, 2))
    print(get_algebraic(87, 2))
    print(get_algebraic(7, 22))
    print(get_algebraic(3, 5))