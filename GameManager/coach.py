from typing import Tuple
import chess



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


            
