from enum import Enum, StrEnum, auto
from typing import Tuple

STARTING_FEN:str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
MAX_RATING:int = 3347

IMAGE_MAP:dict[str, str] = {
        "r": r"assets\imgs\b_rook.png",
        "n": r"assets\imgs\b_knight.png",
        "b": r"assets\imgs\b_bishop.png",
        "q": r"assets\imgs\b_queen.png",
        "k": r"assets\imgs\b_king.png",
        "p": r"assets\imgs\b_pawn.png",
        "R": r"assets\imgs\w_rook.png",
        "N": r"assets\imgs\w_knight.png",
        "B": r"assets\imgs\w_bishop.png",
        "Q": r"assets\imgs\w_queen.png",
        "K": r"assets\imgs\w_king.png",
        "P": r"assets\imgs\w_pawn.png",
    }

class Theme(Enum):
    SMOTHEREDMATE	= (1,"smotheredMate")
    HANGINGPIECE	= (2,"hangingPiece")
    ONEMOVE	= (3,"oneMove")
    SWALLOWSTAILMATE	= (4,"swallowstailMate")
    VERYLONG	= (5,"veryLong")
    ROOKENDGAME	= (6,"rookEndgame")
    MATEIN5	= (7,"mateIn5")
    PIN	= (8,"pin")
    DOUBLEBISHOPMATE	= (9,"doubleBishopMate")
    OPENING	= (10,"opening")
    ZUGZWANG	= (11,"zugzwang")
    LONG	= (12,"long")
    INTERFERENCE	= (13,"interference")
    XRAYATTACK	= (14,"xRayAttack")
    BACKRANKMATE	= (15,"backRankMate")
    ATTRACTION	= (16,"attraction")
    MASTER	= (17,"master")
    MATEIN4	= (18,"mateIn4")
    ADVANTAGE	= (19,"advantage")
    TRIANGLEMATE	= (20,"triangleMate")
    KINGSIDEATTACK	= (21,"kingsideAttack")
    QUEENROOKENDGAME	= (22,"queenRookEndgame")
    QUIETMOVE	= (23,"quietMove")
    ENPASSANT	= (24,"enPassant")
    ENDGAME	= (25,"endgame")
    EXPOSEDKING	= (26,"exposedKing")
    DISCOVEREDCHECK	= (27,"discoveredCheck")
    ATTACKINGF2F7	= (28,"attackingF2F7")
    MATEIN2	= (29,"mateIn2")
    HOOKMATE	= (30,"hookMate")
    PROMOTION	= (31,"promotion")
    MATEIN1	= (32,"mateIn1")
    MASTERVSMASTER	= (33,"masterVsMaster")
    SHORT	= (34,"short")
    SKEWER	= (35,"skewer")
    CRUSHING	= (36,"crushing")
    EQUALITY	= (37,"equality")
    EPAULETTEMATE	= (38,"epauletteMate")
    PAWNENDGAME	= (39,"pawnEndgame")
    BALESTRAMATE	= (40,"balestraMate")
    OPERAMATE	= (41,"operaMate")
    KILLBOXMATE	= (42,"killBoxMate")
    CASTLING	= (43,"castling")
    CAPTURINGDEFENDER	= (44,"capturingDefender")
    INTERMEZZO	= (45,"intermezzo")
    KNIGHTENDGAME	= (46,"knightEndgame")
    TRAPPEDPIECE	= (47,"trappedPiece")
    ADVANCEDPAWN	= (48,"advancedPawn")
    DOUBLECHECK	= (49,"doubleCheck")
    DISCOVEREDATTACK	= (50,"discoveredAttack")
    VUKOVICMATE	= (51,"vukovicMate")
    UNDERPROMOTION	= (52,"underPromotion")
    CORNERMATE	= (53,"cornerMate")
    FORK	= (54,"fork")
    BISHOPENDGAME	= (55,"bishopEndgame")
    CLEARANCE	= (56,"clearance")
    DOVETAILMATE	= (57,"dovetailMate")
    DEFLECTION	= (58,"deflection")
    PILLSBURYSMATE	= (59,"pillsburysMate")
    MATE	= (60,"mate")
    DEFENSIVEMOVE	= (61,"defensiveMove")
    MORPHYSMATE	= (62,"morphysMate")
    MIDDLEGAME	= (63,"middlegame")
    QUEENENDGAME	= (64,"queenEndgame")
    BLINDSWINEMATE	= (65,"blindSwineMate")
    ANASTASIAMATE	= (66,"anastasiaMate")
    COLLINEARMOVE	= (67,"collinearMove")
    SUPERGM	= (68,"superGM")
    ARABIANMATE	= (69,"arabianMate")
    QUEENSIDEATTACK	= (70,"queensideAttack")
    MATEIN3	= (71,"mateIn3")
    BODENMATE	= (72,"bodenMate")
    SACRIFICE	= (73,"sacrifice")

    def __new__(cls, int_val: int, str_val: str):
        # Tie the Enum's base value to the integer
        obj = object.__new__(cls)
        obj._value_ = int_val 
        
        # Assign custom attributes for tracking
        obj.id = int_val        #type: ignore
        obj.label = str_val     #type: ignore
        return obj

    # Fallback to allow implicit string conversions
    def __str__(self) -> str:
        return self.label       #type: ignore



class Skill(Enum):
    EASY = 1
    BEGINNER = 2
    INTRMEDIATE = 3
    ADVANCED = 4
    MASTER = 5
    GRAND_MASTER = 6
    UNKNOWN = 99

SKILL_BUCKETS:dict[Skill, Tuple[int, int]] = {
    Skill.EASY: (0, 799),
    Skill.BEGINNER: (800, 1199),
    Skill.INTRMEDIATE: (1200, 1799),
    Skill.ADVANCED: (1800, 2199),
    Skill.MASTER: (2200, 2499),
    Skill.GRAND_MASTER: (2500, MAX_RATING)
}