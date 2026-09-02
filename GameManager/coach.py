from typing import Tuple, Optional
import chess

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
                 sol:list[chess.Move]):

    our_moves  = ChessCoach.get_legal_moves(board, color)
    
    for m in our_moves:
        board.push(m)
        if board.is_checkmate():
            sol.append(m)
            return

        if board.is_check():
            sol.append(m)
            their_moves:list[chess.Move] = ChessCoach.get_legal_moves(board, not color)   #only moves that will get out of check

            for tm in their_moves:
                board.push(tm)
                check_mating(board, color, sol)
        board.pop()
    

class ChessCoach:
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
                       square:chess.Square)->list[Tuple[chess.Piece, chess.Square]] | None:
        """
        gets protectors for a given square

        
        """
        attack_map:dict[chess.Square, chess.Piece] = {}
        piece = board.piece_at(square)
        
        if piece is not None:
            attack_map =  ChessCoach.get_pieces_attacking(board, piece.color, square)   

    @staticmethod
    def get_attackers(board:chess.Board, 
                      square:chess.Square)->dict[chess.Square, chess.Piece]:
        """
        gets attackers for a given square
        """

        attack_map:dict[chess.Square, chess.Piece] = {}
        piece = board.piece_at(square)
        if piece is not None:
            color:chess.Color = chess.BLACK if piece.color else chess.WHITE
            attack_map = ChessCoach.get_pieces_attacking(board, color, square)

        return attack_map

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
    def mate_in_n(board:chess.Board, 
                    color:chess.Color, 
                    moves:Optional[list[chess.Move]],
                    *,
                    solution:list[chess.Move]=[])->list[chess.Move]:

        def turn_str(c:bool)->str:
            return "White" if c else "Black"

        if board.turn != color:
            raise ValueError(f"Color must match board's turn. color={turn_str(color)}, turn={turn_str( board.turn)}")
        if board.is_checkmate():
            raise ValueError(f"{turn_str(not color)} is already in checkmate.")
                
        
        return []

        

"""
    Are you pinned, can you pin or skewer someone, fork
    who controls the middle
    show move anaysis
    mate in one and maybe two
    load game
    save game
 """


            
