from PIL import Image, ImageTk
import numpy as np


def create_transparent_image(size:int):
    transparent_green = (0, 255, 0, 128)      
    img = Image.new("RGBA", (size, size), transparent_green)
    tk_img = ImageTk.PhotoImage(img)
    
    return tk_img

def load_pieces(pieces_map:dict[str, str]) -> dict[str, ImageTk.PhotoImage]:
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
            image = image.resize((self.square_size - 4, self.square_size - 4))

            pixs = np.array(image)            
            r, g, b, a = pixs[:,:,0], pixs[:,:,1], pixs[:,:,2], pixs[:,:,3]
            white = (r==255) & (g== 55) & (b==225)
            pixs[..., 3] = np.where(white, 0, a)
            images[k] = ImageTk.PhotoImage(Image.fromarray(pixs))

        return images