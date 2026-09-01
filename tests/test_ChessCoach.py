import pytest
from typing import Tuple

import chess
from GameManager import ChessCoach


class TestChessCoach:
    def test_white_attacked_no_protect(self):
        board:chess.Board = chess.Board("rnbqkbnr/1ppppp1p/4P1p1/p7/8/3P4/PPP2PPP/RNBQKBNR b KQkq - 0 1")
        
        at:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_attackers(board, chess.E6)
        pt:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_protectors(board, chess.E6)

        assert at is not None
        assert len(at) == 2
        assert (chess.Piece.from_symbol("p"), chess.F7) in at
        assert (chess.Piece.from_symbol("p"), chess.D7) in at

        assert pt is not None
        assert len(pt) == 0

    def test_white_attacked_with_protect(self):
            board:chess.Board = chess.Board("rnbqkbnr/1ppppp1p/4P1p1/p2P4/8/8/PPP1QPPP/RNB1KBNR b KQkq - 0 1")
            
            at:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_attackers(board, chess.E6)
            pt:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_protectors(board, chess.E6)
    
            assert at is not None
            assert len(at) == 2
            assert (chess.Piece.from_symbol("p"), chess.F7) in at
            assert (chess.Piece.from_symbol("p"), chess.D7) in at
    
            assert pt is not None
            assert len(pt) == 2
            assert (chess.Piece.from_symbol("P"), chess.D5) in pt
            assert (chess.Piece.from_symbol("Q"), chess.E2) in pt

    def test_white_no_attacked_with_protect(self):
            board:chess.Board = chess.Board("rnbqkbnr/1ppppp1p/6p1/p3P3/3P4/8/PPP1QPPP/RNB1KBNR b KQkq - 0 1")
            
            at:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_attackers(board, chess.E5)
            pt:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_protectors(board, chess.E5)
    
            assert at is not None
            assert len(at) == 0

            assert pt is not None
            assert len(pt) == 2
            assert (chess.Piece.from_symbol("P"), chess.D4) in pt
            assert (chess.Piece.from_symbol("Q"), chess.E2) in pt

    def test_black_attacked_no_protect(self):
            board:chess.Board = chess.Board("rnbqkbnr/pp1ppppp/8/8/8/2p5/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            
            at:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_attackers(board, chess.C3)
            pt:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_protectors(board, chess.C3)
    
            assert at is not None
            assert len(at) == 3
            assert (chess.Piece.from_symbol("N"), chess.B1) in at
            assert (chess.Piece.from_symbol("P"), chess.B2) in at
            assert (chess.Piece.from_symbol("P"), chess.D2) in at
    
            assert pt is not None
            assert len(pt) == 0

    def test_black_attacked_with_protect(self):
            board:chess.Board = chess.Board("rnbqk1nr/pp1ppppp/5b2/8/8/2p5/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            
            at:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_attackers(board, chess.C3)
            pt:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_protectors(board, chess.C3)
    
            assert at is not None
            assert len(at) == 3
            assert (chess.Piece.from_symbol("N"), chess.B1) in at
            assert (chess.Piece.from_symbol("P"), chess.B2) in at
            assert (chess.Piece.from_symbol("P"), chess.D2) in at
    
            assert pt is not None
            assert len(pt) == 1
            assert (chess.Piece.from_symbol("b"), chess.F6) in pt

    def test_black_no_attacked_with_protect(self):
            board:chess.Board = chess.Board("rn1qkbnr/pp1ppppp/4b3/8/2p5/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            
            at:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_attackers(board, chess.C4)
            pt:list[Tuple[chess.Piece, chess.Square]] | None = ChessCoach.get_protectors(board, chess.C4)
    
            assert at is not None
            assert len(at) == 0

            assert pt is not None
            assert len(pt) == 1
            assert (chess.Piece.from_symbol("b"), chess.E6) in pt
    

                

    # 


