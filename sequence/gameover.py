#coding: utf8
from OpenGL import GL
import sdl2

from program.const import *
from program.box import BOX
from program import script
from sequence.locals import MenuItems


class GameOver(object):
    def __init__(self):
        self.text = ["Game Over"]
        self.text2 = ["Game Clear!!"]

    def init(self, text):
        self.menu = MenuItems(text, BOX.Y/8, 0.4)

    def mainloop(self, flg=True):
        self.init(self.text if flg else self.text2)
        start = sdl2.SDL_GetTicks()
        while True:
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in KS_ESC:
                        return
                    elif key in KS_RETURN:
                        return
            t = sdl2.SDL_GetTicks()
            if t - start > 2000:
                return
            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
