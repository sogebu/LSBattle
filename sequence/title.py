#coding: utf8
import time
from math import cos

from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from program.text import Sentence, drawSentence
from sequence.locals import MenuItems, backimage

class Title(object):
    PLAY    = 0
    OPTION  = 1
    RANKING = 2
    QUIT    = 3
    def __init__(self):
        self.message = "Press Any Key"
        self.texts = ["Start",
                      "Config",
                      "Ranking",
                      "Quit"]
        self.copyrights = (
            "3D models from http://www.geocities.jp/oirahakobito2/sozai/sozai.html\n"
            "Yukkuri Marisa/Reimu from 2ch and niconico.\n"
            "Milky Way from http://www.eso.org/public/images/eso0932a/\n"
            "Earth and Moon from http://visibleearth.nasa.gov/ etc.\n"
            "The kiloji font from http://www.ez0.net/distribution/font/kiloji/ \n"
            "Einstein from http://www.courseweb.uottawa.ca/Mat4183/"
            )

    def init(self):
        self.title_message = Sentence(self.message, BOX.Y/12)
        # self.menu = MenuItems(self.texts, BOX.Y/12, 0.4,
        #                       title="GAME TITLE WANTED!", title_hight=BOX.Y/8,
        #                       title2="<contact address>", title2_hight=BOX.Y/20,
        #                       title2_color=(0.8, 0.8, 0.8, 1.0), title_color=(1.0, 1.0, 1.0, 1.0))
        self.menu = MenuItems(self.texts, BOX.Y/12, 0.4,
                              title=GAME_NAME, title_hight=BOX.Y/8,
                              title2_color=(0.8, 0.8, 0.8, 1.0), title_color=(1.0, 1.0, 1.0, 1.0))

    def mainloop(self, top=True):
        self.init()
        t = 0.0
        while True:

            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    if top:
                        top = False
                        break
                    key = event.key.keysym.sym
                    if key in KS_ESC:
                        BOX.game_quit()
                    elif key == sdl2.SDLK_UP:
                        self.menu.up()
                    elif key == sdl2.SDLK_DOWN:
                        self.menu.down()
                    elif key in KS_RETURN:
                        return self.menu.choice
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse = event.button
                    if mouse.button == 1:
                        if top:
                            top = False
                            break
                        choice = self.menu.mouse_check(mouse.x, mouse.y)
                        if 0 <= choice:
                            return choice

            if top:
                backimage.draw(False)
                t = sdl2.SDL_GetTicks()
                self.title_message.draw_center(color=(1.0, 0.0, 0.0, abs(cos(t*0.0015))))
                GL.glColor(0.7, 0.7, 0.7, 1.0)
                n = 60.0
                drawSentence(self.copyrights, BOX.Y/n, 0, BOX.Y*6/n)
            else:
                backimage.draw()
                self.menu.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)

