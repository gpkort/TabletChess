import pytest
from typing import Tuple

import chess
from GameManager import ChessCoach


class TestChessCoach:
    """
    unit test for ChessCoach

    great tool from creating FENs
    https://www.redhotpawn.com/chess-tools/chess-fen-viewer
    """
    def test_white_attacked_no_protect(self):
        board:chess.Board = chess.Board("rnbqkbnr/1ppppp1p/4P1p1/p7/8/3P4/PPP2PPP/RNBQKBNR b KQkq - 0 1")
        
        at:dict[chess.Square, chess.Piece] = ChessCoach.get_attackers(board, chess.E6)
        pt:dict[chess.Square, chess.Piece] = ChessCoach.get_protectors(board, chess.E6)

        assert len(at) == 2
        assert at.get(chess.F7) == chess.Piece.from_symbol("p")
        assert at.get(chess.D7) == chess.Piece.from_symbol("p")

        assert len(pt) == 0

    def test_white_attacked_with_protect(self):
            board:chess.Board = chess.Board("rnbqkbnr/1ppppp1p/4P1p1/p2P4/8/8/PPP1QPPP/RNB1KBNR b KQkq - 0 1")
            
            at:dict[chess.Square, chess.Piece] = ChessCoach.get_attackers(board, chess.E6)
            pt:dict[chess.Square, chess.Piece] = ChessCoach.get_protectors(board, chess.E6)
    
            assert len(at) == 2
            assert at.get(chess.F7) == chess.Piece.from_symbol("p")
            assert at.get(chess.D7) == chess.Piece.from_symbol("p")
    
            assert len(pt) == 2
            assert pt.get(chess.D5) == chess.Piece.from_symbol("P")
            assert pt.get(chess.E2) == chess.Piece.from_symbol("Q")

    def test_white_no_attacked_with_protect(self):
            board:chess.Board = chess.Board("rnbqkbnr/1ppppp1p/6p1/p3P3/3P4/8/PPP1QPPP/RNB1KBNR b KQkq - 0 1")
            
            at:dict[chess.Square, chess.Piece] = ChessCoach.get_attackers(board, chess.E5)
            pt:dict[chess.Square, chess.Piece] = ChessCoach.get_protectors(board, chess.E5)
    
            assert len(at) == 0

            assert len(pt) == 2
            assert pt.get(chess.D4) == chess.Piece.from_symbol("P")
            assert pt.get(chess.E2) == chess.Piece.from_symbol("Q")

    def test_black_attacked_no_protect(self):
            board:chess.Board = chess.Board("rnbqkbnr/pp1ppppp/8/8/8/2p5/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            
            at:dict[chess.Square, chess.Piece] = ChessCoach.get_attackers(board, chess.C3)
            pt:dict[chess.Square, chess.Piece] = ChessCoach.get_protectors(board, chess.C3)
    
            assert at is not None
            assert len(at) == 3
            assert at.get(chess.B1) == chess.Piece.from_symbol("N")
            assert at.get(chess.B2) == chess.Piece.from_symbol("P")
            assert at.get(chess.D2) == chess.Piece.from_symbol("P")

            assert len(pt) == 0

    def test_black_attacked_with_protect(self):
            board:chess.Board = chess.Board("rnbqk1nr/pp1ppppp/5b2/8/8/2p5/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            
            at:dict[chess.Square, chess.Piece] = ChessCoach.get_attackers(board, chess.C3)
            pt:dict[chess.Square, chess.Piece] | None = ChessCoach.get_protectors(board, chess.C3)
    
            assert len(at) == 3
            assert at.get(chess.B1) == chess.Piece.from_symbol("N")
            assert at.get(chess.B2) == chess.Piece.from_symbol("P")
            assert at.get(chess.D2) == chess.Piece.from_symbol("P")
    
            assert len(pt) == 1
            assert pt.get(chess.F6) == chess.Piece.from_symbol("b")

    def test_black_no_attacked_with_protect(self):
            board:chess.Board = chess.Board("rn1qkbnr/pp1ppppp/4b3/8/2p5/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            
            at:dict[chess.Square, chess.Piece] = ChessCoach.get_attackers(board, chess.C4)
            pt:dict[chess.Square, chess.Piece] = ChessCoach.get_protectors(board, chess.C4)
    
            assert len(at) == 0

            assert len(pt) == 1
            assert pt.get(chess.E6) == chess.Piece.from_symbol("b")

            #1R6/5p2/1R5k/Q7/8/8/8/Q7 b - - 0 1

    def test_simple_mate_in_one(self):
       board:chess.Board = chess.Board("1R6/5p2/7k/QR6/8/8/8/K7 w - - 0 1")
                                       #'7R/5pk1/8/QR6/8/8/8/K7 w - - 2 2'
       solutions:list[list[chess.Move]] = ChessCoach.mate_in_n(board, chess.WHITE) 

       assert len(solutions) == 0
       print(solutions)    
       


