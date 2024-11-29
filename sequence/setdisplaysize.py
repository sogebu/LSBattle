#coding: utf8
from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from program.text import MyFont
from program import script
from sequence.locals import MenuItems, backimage


class SetDisplaySize(object):
    def init(self):
        self.texts = ["%i * %i"%size for size in disp_sizes]
        if not BOX.FULL_SCREEN:
            self.texts.append("Full Screen")
        self.menu = MenuItems(self.texts, BOX.Y/12, ret=True, title="Display Size")
        if not BOX.FULL_SCREEN:
            self.menu.choice = disp_sizes.index((BOX.X, BOX.Y))

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
                if choice < len(disp_sizes):
                    BOX.set_displaysize(choice)
                elif choice == self.menu.RETURN:
                    return
                else:
                    BOX.set_fullscreen()
                backimage.load()
                MyFont.init_font(script.ui.font.name)
                self.init()
                return

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
