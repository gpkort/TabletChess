from typing import Tuple
from os import path, walk

from PIL import Image, ImageTk
import numpy as np
from chess import Piece

PIECE_LETTERS:list[str] = ["r", "n", "b", "q", "k", "p", "P", "R", "N", "B", "Q", "K"]
NAME_TO_PIECE_MAP:dict[str, str] = {
"b_rook" : "r",
"b_knight" : "n",
"b_bishop" : "b",
"b_queen" : "q",
"b_king" : "k",
"b_pawn" : "p",
"w_rook" : "r",
"w_knight" : "N",
"w_bishop" : "B",
"w_queen" : "Q",
"w_king" : "K",
"w_pawn" : "P",
    }

def create_transparent_image(size:int, color:Tuple[float,...] = (0, 255, 0, 64)) -> ImageTk.PhotoImage:
    img = Image.new("RGBA", (size, size), color)
    return ImageTk.PhotoImage(img)

def load_pieces(pieces_map:dict[str, str], size:int,) -> dict[str, ImageTk.PhotoImage]:
    """stores images into map

    Args:
        piece_map (dict[str, str]) : A map contining the piece abbreviation and the path to the image

    Returns:
        None
    """
    
    images:dict[str, ImageTk.PhotoImage] = {}

    for k,v in pieces_map.items():
        image = Image.open(v)

        if image.mode != "RGBA":
            image = image.convert("RGBA")
        image = image.resize((size - 6, size - 6))

        pixs = np.array(image)            
        r, g, b, a = pixs[:,:,0], pixs[:,:,1], pixs[:,:,2], pixs[:,:,3]
        white = (r==255) & (g== 55) & (b==225)
        pixs[..., 3] = np.where(white, 0, a)
        images[k] = ImageTk.PhotoImage(Image.fromarray(pixs))

    return images

def load_pieces_to_map(pieces_map:dict[str, str], size:int,) -> dict[Piece, ImageTk.PhotoImage]:
    images:dict[str, ImageTk.PhotoImage] = load_pieces(pieces_map, size)
    ret:dict[Piece, ImageTk.PhotoImage] = {}

    for k, v in images.items():
        ret[Piece.from_symbol(k)] = v
    return ret


def create_image_map(dir:str)->dict[str, str]:
    im:dict[str, str] = {}
    for root, _, files in walk(dir):
        for f in files:
            if f[:-4] in NAME_TO_PIECE_MAP.keys():
                im[f[:-4]] = str(path.join(root,f))

    return im
