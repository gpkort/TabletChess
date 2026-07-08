import tkinter as tk
from PIL import Image, ImageTk

class SquareInfo:
    YELLOW:str = "#FFFF00"
    GREEN:str = "#785DB7"
    def __init__(self,
                 canvas:tk.Canvas,
                 name:str,
                 x:int,
                 y:int,
                 size:int,
                 move_image:ImageTk.PhotoImage,
                 *,
                 image:ImageTk.PhotoImage | None = None):

        self._canvas:tk.Canvas = canvas
        self._x:int = x
        self._y:int = y
        self._size = size
        self._image:ImageTk.PhotoImage | None = image
        self._name:str = name
        self._image_id:int = -1
        self._rect_id:int = -1
        self._circ_id:int = -1
        self._move_id:int = -1

    @property
    def name(self):
        """ 
            gets algebraic name of square
        Returns:
            str: name
        """
        return self._name
    @property
    def x(self)->int:
        return self._x
    @property
    def y(self)->int:
        return self._y
    @property
    def image(self) -> ImageTk.PhotoImage | None:
        return self._image
    @property
    def selected(self) -> bool:
        return self._rect_id != -1
    @selected.setter
    def selected(self, value:bool):
        if value == self._rect_id != -1:
            return

        if value:
            self._rect_id = self._canvas.create_rectangle(self._x,
                                          self._y,
                                          self._x + self._size,
                                          self._y + self._size,
                                          width=2,
                                          outline=self.YELLOW
                                          )
        else:
            self._canvas.delete(self._rect_id)
            self._rect_id = -1
    @property
    def legal(self)-> bool:
        return self._circ_id != -1    
    @legal.setter
    def legal(self, value:bool):
        if value == self._circ_id != -1:
            return
        if value:
            self._circ_id = self._canvas.create_oval(self._x + 4,
                                          self._y + 4,
                                          self._x + self._size - 8,
                                          self._y + self._size - 8,
                                          width=0.0,
                                          fill=self.GREEN)
        else:
            self._canvas.delete(self._circ_id)
            self._circ_id = -1
    
    @property
    def show_move(self)->bool:
        return self._move_id != -1

    def show_image(self):
        if self._image_id != -1:
            self._canvas.delete(self._image_id)
            self._image_id = -1

        # pylint: disable=pointless-statement
        self._image_id = self._canvas.create_image(self.x + 2,
                                                self.y + 2,
                                                anchor=tk.NW,
                                                image=self._image)

    def set_image(self, img:ImageTk.PhotoImage, show:bool = False):
        self._image = img
        self._image_id = -1
        if show:
            self.show_image()
    
    def kill(self)->ImageTk.PhotoImage | None:
        if self._image_id != -1:
            self._canvas.delete(self._image_id)
            self._image_id = -1

        tempImage:ImageTk.PhotoImage | None = self._image
        self._image = None

        return tempImage
    
    # def clear()