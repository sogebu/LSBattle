#coding: utf8
from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from program.text import Sentence
from program import script
from sequence.locals import MenuItems


class ContineQuestion(object):
    YES = 0
    NO  = 1
    def __init__(self):
        self.n = 0

    def init(self):
        n = script.game.continue_num - self.n
        self.menu = MenuItems(["Yes", "No"], BOX.Y/10,
                              between_lines=1, ofy=-BOX.Y*0.1,
                              title="Continue?",
                              title2="(%i %s left)"%(n, 'lives' if n > 1 else 'life'))

    def mainloop(self):
        self.init()
        while True:
            choice = -1
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in KS_ESC:
                        return self.NO
                    elif key == sdl2.SDLK_UP:
                        self.menu.up()
                    elif key  == sdl2.SDLK_DOWN:
                        self.menu.down()
                    elif key in KS_RETURN:
                        choice = self.menu.choice
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse = event.button
                    if mouse.button == 1:
                        choice = self.menu.mouse_check(mouse.x, mouse.y)
                        break

            if choice == self.YES:
                self.n += 1
                return self.YES
            elif choice == self.NO:
                return self.NO

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)

