#coding: utf8
# manuitems.py
from OpenGL import GL

from program.box import BOX
from program.text import Sentence


class M(object):
    CENTER      = 0
    TOP         = 1
    BOTTOM      = 2
    RIGHT_RIGHT = 3
    RIGHT_LEFT  = 4
    LEFT_RIGHT  = 5
    LEFT_LEFT   = 6


class MenuItems(object):
    def __init__(self, texts, height, between_lines=0.3,
                 row=M.CENTER, colum=M.CENTER, ofx=0, ofy=0, ret=False,
                 title=None, title2=None,
                 title_hight=None, title2_hight=None,
                 title_color=(1,1,1,1), title2_color=(1,1,1,1)):
        self.texts = [Sentence(text, height) for text in texts]
        self.height = height
        self.between_lines = height * between_lines
        self.n = len(texts)
        self.choice = 0

        dY = height*self.n + self.between_lines*(self.n-1)
        if row == M.CENTER:
            y = (BOX.Y + dY)*0.5 + self.between_lines + ofy
        elif row == M.TOP:
            y = BOX.Y - self.between_lines*3 + ofy
        elif row == M.BOTTOM:
            y = dY + self.between_lines*3 + ofy
        else:
            y = ofy

        self._fx = {M.CENTER:     lambda w:(BOX.X - w)*0.5                    + ofx,
                    M.LEFT_LEFT:  lambda w:self.between_lines*3               + ofx,
                    M.LEFT_RIGHT: lambda w:BOX.X*0.5 - w - self.between_lines + ofx,
                    M.RIGHT_LEFT: lambda w:BOX.X*0.5 + self.between_lines     + ofx,
                    M.RIGHT_RIGHT:lambda w:BOX.X - w - self.between_lines*3   + ofx}
        self.fx = self._fx[colum]
        self.pos = []
        for i in range(self.n):
            x = self.fx(self.texts[i].width)
            self.pos.append([x, y])
            y -= height + self.between_lines

        if ret:
            if height > BOX.Y/12:
                height = BOX.Y/12
            text = Sentence("Return", height)
            self.n += 1
            self.texts.append(text)
            x = BOX.X - text.width - self.between_lines*3
            y = height + self.between_lines*3
            self.pos.append([x, y])
            self.RETURN = self.n - 1

        self.title_color = title_color
        self.title2_color = title2_color
        if title is not None:
            if title_hight is None:
                if height < BOX.Y/10:
                    title_hight = BOX.Y/10
                else:
                    title_hight = height
            self.title = Sentence(title, title_hight)
            x = (BOX.X - self.title.width)*0.5
            y = BOX.Y - title_hight*0.2
            self.title_pos = [x, y]
        else:
            self.title = None

        if title2 is not None:
            if title2_hight is None:
                if height < BOX.Y/10:
                    title2_hight = BOX.Y/10
                else:
                    title2_hight = height
            self.title2 = Sentence(title2, title2_hight)
            x = (BOX.X - self.title2.width)*0.5
            y = BOX.Y - title_hight*1.2
            self.title2_pos = [x, y]
        else:
            self.title2 = None

    def mouse_check(self, x, y):
        y = BOX.Y - y
        h = self.height
        for i in range(self.n):
            ox, oy = self.pos[i]
            w = self.texts[i].width
            if ox < x < ox+w and oy-h < y < oy:
                self.choice = i
                return i
        return -1

    def up(self):
        self.choice = (self.choice - 1)%self.n

    def down(self):
        self.choice = (self.choice + 1)%self.n

    def replace(self, index, text):
        self.texts[index] = Sentence(text, self.height)
        self.pos[index][0] = self.fx(self.texts[index].width)

    def repos_colum(self, index, colum, ofx=0):
        self.pos[index][0] = self._fx[colum](self.texts[index].width) + ofx

    def draw(self, focus=None):
        if focus is None:
            focus = (1.0, 0.15, 0.0, 1.0)
        for i in range(self.n):
            if i == self.choice:
                GL.glColor(*focus)
            else:
                GL.glColor(0.8, 0.8, 0.8, 1.0)
            x, y = self.pos[i]
            self.texts[i].draw(x, y)

        if self.title is not None:
            GL.glColor(self.title_color)
            self.title.draw(*self.title_pos)
        if self.title2 is not None:
            GL.glColor(self.title2_color)
            self.title2.draw(*self.title2_pos)
