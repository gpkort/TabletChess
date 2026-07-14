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

class Theme(StrEnum):
    SMOTHEREDMATE = auto()
    HANGINGPIECE = auto()
    ONEMOVE = auto()
    SWALLOWSTAILMATE = auto()
    VERYLONG = auto()
    ROOKENDGAME = auto()
    MATEIN5 = auto()
    PIN = auto()
    DOUBLEBISHOPMATE = auto()
    OPENING = auto()
    ZUGZWANG = auto()
    LONG = auto()
    INTERFERENCE = auto()
    XRAYATTACK = auto()
    BACKRANKMATE = auto()
    ATTRACTION = auto()
    MASTER = auto()
    MATEIN4 = auto()
    ADVANTAGE = auto()
    TRIANGLEMATE = auto()
    KINGSIDEATTACK = auto()
    QUEENROOKENDGAME = auto()
    QUIETMOVE = auto()
    ENPASSANT = auto()
    ENDGAME = auto()
    EXPOSEDKING = auto()
    DISCOVEREDCHECK = auto()
    ATTACKINGF2F7 = auto()
    MATEIN2 = auto()
    HOOKMATE = auto()
    PROMOTION = auto()
    MATEIN1 = auto()
    MASTERVSMASTER = auto()
    SHORT = auto()
    SKEWER = auto()
    CRUSHING = auto()
    EQUALITY = auto()
    EPAULETTEMATE = auto()
    PAWNENDGAME = auto()
    BALESTRAMATE = auto()
    OPERAMATE = auto()
    KILLBOXMATE = auto()
    CASTLING = auto()
    CAPTURINGDEFENDER = auto()
    INTERMEZZO = auto()
    KNIGHTENDGAME = auto()
    TRAPPEDPIECE = auto()
    ADVANCEDPAWN = auto()
    DOUBLECHECK = auto()
    DISCOVEREDATTACK = auto()
    VUKOVICMATE = auto()
    UNDERPROMOTION = auto()
    CORNERMATE = auto()
    FORK = auto()
    BISHOPENDGAME = auto()
    CLEARANCE = auto()
    DOVETAILMATE = auto()
    DEFLECTION = auto()
    PILLSBURYSMATE = auto()
    MATE = auto()
    DEFENSIVEMOVE = auto()
    MORPHYSMATE = auto()
    MIDDLEGAME = auto()
    QUEENENDGAME = auto()
    BLINDSWINEMATE = auto()
    ANASTASIAMATE = auto()
    COLLINEARMOVE = auto()
    SUPERGM = auto()
    ARABIANMATE = auto()
    QUEENSIDEATTACK = auto()
    MATEIN3 = auto()
    BODENMATE = auto()
    SACRIFICE = auto()

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