# coding: utf8
# text.py
import os

from OpenGL.GL import *

from program.box import BOX
from program.const import IMG_DIR
from program.utils import load_texture, FlatScreen


_OFFSET = 32
class MyFont(object):
    c_map = [[0, 0]for i in range(_OFFSET, 127)]
    name = ""
    height = 0
    size = 512.0
    tw = 1
    texture_id = 0
    @classmethod
    def init_font(cls, font):
        if font != cls.name:
            cls.delete()
        if cls.texture_id == 0 or not glIsTexture(cls.texture_id):
            if os.path.isfile(os.path.join(IMG_DIR, "font", font+".font")):
                path = os.path.join(IMG_DIR, "font", font)
            else:
                path = os.path.join(IMG_DIR, font)
            f = open(path+".font")

            name, size, height = f.readline().split()
            if name != font:
                raise IOError("%sfont is not available"%font)
            cls.name = name
            cls.size = float(size)
            cls.height = float(height) / cls.size

            for line in f:
                c, tx, ty, tw = [int(i) for i in line.split()]
                cls.c_map[c-_OFFSET][0] = tx / cls.size
                cls.c_map[c-_OFFSET][1] = 1.0 - ty / cls.size
            cls.tw = tw / cls.size
            cls.twh = cls.tw / cls.height

            cls.texture_id = load_texture(path+".png")

    @classmethod
    def delete(cls):
        if cls.texture_id != 0 and glIsTexture(cls.texture_id):
            glDeleteTextures(cls.texture_id)
            cls.texture_id = 0

    @classmethod
    def draw(cls, c, x, y, w, h):
        tx, ty = cls.c_map[c-_OFFSET]
        tw = cls.tw
        th = cls.height
        glTexCoord(tx,    ty-th); glVertex(x,   y-h)
        glTexCoord(tx+tw, ty-th); glVertex(x+w, y-h)
        glTexCoord(tx+tw, ty);    glVertex(x+w, y)
        glTexCoord(tx,    ty);    glVertex(x,   y)

    @classmethod
    def draw3d(cls, c, x, y, z, w, h, dx1, dy1, dz1, dx2, dy2, dz2):
        tx, ty = cls.c_map[c-_OFFSET]
        tw = cls.tw
        th = cls.height
        glTexCoord(tx,    ty-th); glVertex(x    -dx2, y    -dy2, z    -dz2)
        glTexCoord(tx+tw, ty-th); glVertex(x+dx1-dx2, y+dy1-dy2, z+dz1-dz2)
        glTexCoord(tx+tw, ty);    glVertex(x+dx1,     y+dy1,     z+dz1)
        glTexCoord(tx,    ty);    glVertex(x,         y,         z)

class Sentence(object):

    def __init__(self, sentence, height):
        if isinstance(sentence, str):
            self.text = [ord(c) for c in sentence]
        else:
            self.text = list(sentence)
        self.height = height
        self.width = len(self.text) * height * MyFont.twh

    def draw(self, x, y, color=None):
        if color is not None:
            glColor(*color)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, MyFont.texture_id)
        FlatScreen.push()
        glBegin(GL_QUADS)
        w = self.height * MyFont.twh
        for c in self.text:
            MyFont.draw(c, x, y, w, self.height)
            x += w
        glEnd()
        FlatScreen.pop()
        glDisable(GL_TEXTURE_2D)

    def draw_center(self, color=None):
        x = (BOX.X - self.width)*0.5
        y = (BOX.Y + self.height)*0.5
        self.draw(x, y, color)

    def draw_center_row(self, y, color=None):
        x = (BOX.X - self.width)*0.5
        self.draw(x, y, color)


def drawSentence(sentence, height, x, y, step=1.0):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, MyFont.texture_id)
    FlatScreen.push()
    glBegin(GL_QUADS)
    w = height * MyFont.twh
    xx = x
    for c in sentence:
        if c == "\n":
            y -= height * step
            xx = x
        else:
            MyFont.draw(ord(c), xx, y, w, height)
            xx += w
    glEnd()
    FlatScreen.pop()
    glDisable(GL_TEXTURE_2D)


def drawSentence3d(sentence, height, pos, m):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, MyFont.texture_id)
    glBegin(GL_QUADS)
    w = height * MyFont.twh
    dx1, dy1, dz1 = m.get_rotate([w, 0.0, 0.0])
    dx2, dy2, dz2 = m.get_rotate([0.0, height, 0.0])
    width = len(sentence) * w
    x = pos.x - dx1 * width * 0.5
    y = pos.y - dy1 * width * 0.5
    z = pos.z - dz1 * width * 0.5
    for c in sentence:
        w = MyFont.draw3d(ord(c), x, y, z, w, height, dx1, dy1, dz1, dx2, dy2, dz2)
        x += dx1
        y += dy1
        z += dz1
    glEnd()
    glDisable(GL_TEXTURE_2D)
