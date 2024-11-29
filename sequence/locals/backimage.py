#coding: utf8
# backimage.py
import sys

from OpenGL.GL import *
import sdl2

from program.box import BOX
from program.utils import load_texture, search_imagefile, FlatScreen
from program import script


class BackImage(object):
    def load(self):
        if script.ui.backimage.image is None:
            self.draw = self._draw_only_clear
        else:
            self.draw = self._draw_image
            path = search_imagefile(script.ui.backimage.image)
            texture_info = load_texture(path, id_only=False)
            self.texture_id = texture_info.texture_id
            width = texture_info.width
            height = texture_info.height
            if script.ui.backimage.image_fill_mode == "FILL":
                dx = dy = tx = ty = 0.0
            elif script.ui.backimage.image_fill_mode == "ALIGN":
                tx = ty = 0.0
                if BOX.X*1.0/BOX.Y > width*1.0/height:
                    dx = (BOX.X  - width * BOX.Y * 1.0 / height) * 0.5
                    dy = 0.0
                else:
                    dx = 0.0
                    dy = (BOX.Y - height * BOX.X * 1.0 / width) * 0.5
            elif script.ui.backimage.image_fill_mode == "CUT":
                dx = dy = 0.0
                if BOX.X*1.0/BOX.Y > width*1.0/height:
                    tx = 0.0
                    ty = (1.0 - width * BOX.Y * 1.0 / (height * BOX.X)) * 0.5
                else:
                    tx = (1.0 - height * BOX.X * 1.0 / (width * BOX.Y)) * 0.5
                    ty = 0.0
            self.vertices = (GLfloat*8)(dx,       dy,
                                        BOX.X-dx, dy,
                                        BOX.X-dx, BOX.Y-dy,
                                        dx,       BOX.Y-dy)
            self.texcoord = (GLfloat*8)(tx,     ty,
                                        1.0-tx, ty,
                                        1.0-tx, 1.0-ty,
                                        tx,     1.0-ty)
            self.color = script.ui.backimage.image_color

    def _draw_only_clear(self, a=True):
        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)

    def _draw_image(self, a=True):
        glClear(GL_DEPTH_BUFFER_BIT|GL_COLOR_BUFFER_BIT)
        r, g, b, aa = self.color
        if a:
            glColor(r, g, b, aa*script.ui.backimage.alpha)
        else:
            glColor(r, g, b, aa)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        FlatScreen.push()
        glVertexPointer(2,   GL_FLOAT, 0, self.vertices)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcoord)
        glDrawArrays(GL_QUADS, 0, 4)
        FlatScreen.pop()
        glDisable(GL_TEXTURE_2D)
