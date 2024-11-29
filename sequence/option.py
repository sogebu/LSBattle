#coding: utf8
from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from sequence.locals import MenuItems, backimage
from sequence.keyconfig import KeyConfig
from sequence.setdisplaysize import SetDisplaySize


class Option(object):
    def __init__(self):
        self.texts = ["Key Config",
                      "Display Size"]
        self.goto = [KeyConfig(),
                     SetDisplaySize()]

    def init(self):
        self.menu = MenuItems(self.texts, BOX.Y/10, ret=True, title="Option")

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
                        if self.menu.choice == self.menu.RETURN:
                            return
                        else:
                            choice = self.menu.RETURN
                        break
                    elif key == sdl2.SDLK_UP:
                        self.menu.up()
                    elif key == sdl2.SDLK_DOWN:
                        self.menu.down()
                    elif key in KS_RETURN:
                        choice = self.menu.choice
                        break
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse = event.button
                    if mouse.button == 1:
                        choice = self.menu.mouse_check(mouse.x, mouse.y)
                        break

            if 0 <= choice:
                if choice == self.menu.RETURN:
                    return
                else:
                    self.goto[choice].mainloop()
                    self.init()
                    #self.menu.choice = self.menu.RETURN

            backimage.draw()
            self.menu.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
