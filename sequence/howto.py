#coding: utf8
from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from sequence.locals import Keys, MenuItems, M


class Howto(object):
    def __init__(self, level):
        self.keys = Keys()
        self.keys.load_map()
        texts1 = []
        texts2 = []
        for name, key in self.keys:
            if level.enabled(name):
                texts1.append(self.keys.name2[self.keys.names.index(name)])
                texts2.append(self.keys.key_map[key])
        texts1 += ["", "Exit          "]
        texts2 += ["", "ESC"]
        n = len(texts1)
        size = BOX.Y*0.6 / n
        self.menu_1 = MenuItems(texts1, size, 0.15,
                                colum=M.LEFT_RIGHT,
                                title="Key Bindings")
        self.menu_2 = MenuItems(texts2, size, 0.15,
                                colum=M.RIGHT_LEFT,)
        self.menu_2.choice = self.menu_1.choice = -1

    def mainloop(self):
        while True:
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    return
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    return

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu_1.draw()
            self.menu_2.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
