from typing import Tuple, Optional
from enum import Enum
import chess

class CheckStatus(Enum):
    DEADEND = 0
    CHECK = 1
    CHECKMATE = 2
    UNKNOWN = 99

def gives_checkmate(board:chess.Board, move: chess.Move) -> bool:
    """
    Probes if the given move would put the opponent in checkmate. The move
    must be at least pseudo-legal.
    chess documentation says this exists in Board class but it does not
    """
    board.push(move)
    try:
        return board.is_checkmate()
    finally:
        board.pop()


def check_mating(board:chess.Board,
                 color:chess.Color,
                 move:chess.Move,
                 solution_stack:list[chess.Move],
                 max_tries:int, current_tries:int)->bool:
    
    print(f"Current: {current_tries}, max: {max_tries}")
    if current_tries == max_tries:
        return False
                
    try:
        if gives_checkmate(board, move):
            solution_stack.append(move)
            return True
    except AssertionError as ae:
        print(f"lan 35 - fen: {board.fen()}")
        print(f"Try: {current_tries}")
        print([m.uci() for m in solution_stack])
        raise ae

    current_tries += 1
    try:
        if board.gives_check(move):
            solution_stack.append(move)

            try:
                board.push(move)
            except AssertionError as ae:
                print(f"lan 35 - fen: {board.fen()}")
                print(f"Try: {current_tries}")
                print([m.uci() for m in solution_stack])
                raise ae
            #only moves that will get out of check
            tmoves:list[chess.Move] = ChessCoach.get_legal_moves(board, not color)

            for tm in tmoves:
                if board.turn == (not color):
                    solution_stack.append(tm)
                    board.push(tm)
                    mvs:list[chess.Move] = ChessCoach.get_legal_moves(board, color)
                    omoves:list[chess.Move] = [m for m in mvs if board.gives_check(m) or
                                                                gives_checkmate(board, m)]

                    for om in omoves:
                        if check_mating(board, color, om, solution_stack, max_tries, current_tries):
                            return True

                    board.pop()
                    solution_stack.pop()
            board.pop()
            solution_stack.pop()
    except AssertionError as ae:
        print(f"lan 35 - fen: {board.fen()}")
        print(f"Try: {current_tries}")
        print([m.uci() for m in solution_stack])
        raise ae
    return False

class ChessCoach:
    """
    Non chess engine chess coach
    """
    @staticmethod
    def get_pieces_attacking(board:chess.Board,
                        color:chess.Color,
                        square:chess.Square)->dict[chess.Square, chess.Piece]:

        attack_map:dict[chess.Square, chess.Piece] = {}

        for s in list(board.attackers(color, square)):
            p:chess.Piece|None = board.piece_at(s)
            if p is not None:
                attack_map[s] = p

        return attack_map

    @staticmethod
    def get_protectors(board:chess.Board, 
                       square:chess.Square)->dict[chess.Square, chess.Piece]:
        """
        gets protectors for a given square        
        """
        piece = board.piece_at(square)

        if piece is not None:
            return ChessCoach.get_pieces_attacking(board, piece.color, square)  
        return {}

    @staticmethod
    def get_attackers(board:chess.Board, 
                      square:chess.Square)->dict[chess.Square, chess.Piece]:
        """
        gets attackers for a given square
        """

        piece = board.piece_at(square)
        if piece is not None:
            color:chess.Color = chess.BLACK if piece.color else chess.WHITE
            return ChessCoach.get_pieces_attacking(board, color, square)

        return {}

    @staticmethod
    def get_potential_captures(board:chess.Board, move:chess.Move, piece:chess.Piece)->dict[chess.Square, chess.Piece]:
        board.push(move)
        attack_map:dict[chess.Square, chess.Piece] =  ChessCoach.get_pieces_attacking(board, 
                                                                                      piece.color,
                                                                                      move.to_square)
        board.pop()
        return attack_map

    @staticmethod
    def get_pieces(board:chess.Board, color:chess.Color)->dict[chess.Square, chess.Piece]:
        pieces:dict[chess.Square, chess.Piece] = {}

        for s, p in board.piece_map().items():
            if p.color == color:
                pieces[s] = p

        return pieces

    @staticmethod
    def get_pinned(board:chess.Board, color:chess.Color)->dict[chess.Square, chess.Piece]:
        pinned:dict[chess.Square, chess.Piece] = {}

        for s, p in ChessCoach.get_pieces(board, color).items():
            if board.is_pinned(color, s):
                pinned[s] = p

        return pinned
    
    @staticmethod
    def pin_squares(board:chess.Board, move:chess.Move)->list[chess.Square]:
        pc:Optional[chess.Color] = board.color_at(move.from_square)
        pins:list[chess.Square] = []

        if pc is not None:
            board.push(move)
            pins = list[board.pin(chess.BLACK if pc else chess.WHITE,  move.to_square)] #type: ignore

        return pins

    @staticmethod
    def get_legal_moves(board:chess.Board, color:chess.Color)->list[chess.Move]:
        lm:list[chess.Move] = []
        
        for s, p in ChessCoach.get_pieces(board, color).items():
            for m in board.legal_moves:
                if s == m.from_square:
                    lm.append(m)

        return lm

    @staticmethod
    def get_checks(board:chess.Board, color:chess.Color)->dict[chess.Square, chess.Move]:
        chk:dict[chess.Square, chess.Move] = {}

        for m in ChessCoach.get_legal_moves(board, color):
            if board.gives_check(m):
                chk[m.from_square] = m

        return chk
   
    @staticmethod
    def mate_in_n(board:chess.Board, color:chess.Color, max_tries:int=10)->list[list[chess.Move]]:

        def turn_str(c:bool)->str:
            return "White" if c else "Black"

        # board = board.copy()
        if board.turn != color:
            raise ValueError(f"Color must match board's turn. color={turn_str(color)}, turn={turn_str( board.turn)}")
        if board.is_checkmate():
            raise ValueError(f"{turn_str(not color)} is already in checkmate.")

        ret:list[list[chess.Move]] = []

        c_moves:list[chess.Move] = [m for m in ChessCoach.get_legal_moves(board, color) 
                                        if board.gives_check(m) or gives_checkmate(board, m)]
        for lm in c_moves:
            stack:list[chess.Move] = []
            bd:chess.Board = board.copy()

            if check_mating(bd, color, lm, stack, max_tries, 0):
                ret.append(stack)
        
        return ret
        

"""
    Are you pinned, can you pin or skewer someone, fork
    who controls the middle
    show move anaysis
    mate in one and maybe two
    load game
    save game
 """


            
