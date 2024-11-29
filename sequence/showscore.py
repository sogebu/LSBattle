#coding: utf8
from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from sequence.locals import MenuItems, M

class ShowScore(object):
    TITLE = 0
    NEXT  = 1
    def __init__(self, score):
        text1, text2, text3 = score.get_text()
        text1 = [""] + text1 + ["", ""]
        text2 = [""] + text2 + ["", "Press Enter for Next, Esc for Title"]
        text3 = [""] + text3 + ["", ""]

        self.menu_1 = MenuItems(text1, BOX.Y/15, 0.2, colum=M.LEFT_LEFT,
                                title="Stage %i clear bonus"%score.stage)
        self.menu_2 = MenuItems(text2, BOX.Y/15, 0.2, colum=M.RIGHT_RIGHT,
                                ofx=-BOX.X/3)
        self.menu_3 = MenuItems(text3, BOX.Y/15, 0.2, colum=M.RIGHT_RIGHT)

        self.menu_1.choice = -1

        self.menu_2.repos_colum(-1, M.CENTER, BOX.X/3)
        self.menu_2.choice = self.menu_2.n - 1

        self.menu_3.choice = self.menu_3.n - 3

    def mainloop(self):
        last_tick = sdl2.SDL_GetTicks()
        while True:
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in KS_RETURN:
                        return self.NEXT
                    elif key in KS_ESC:
                        return self.TITLE
                    else:
                        return self.NEXT
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse = event.button
                    if mouse.button == 1:
                        return self.NEXT
            if sdl2.SDL_GetTicks() - last_tick > 3000:
                return self.NEXT

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu_1.draw(focus=(1.0, 1.0, 1.0, 1.0))
            self.menu_2.draw(focus=(1.0, 1.0, 1.0, 1.0))
            self.menu_3.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
