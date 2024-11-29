#coding: utf8
import time

from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from sequence.locals import MenuItems
from sequence.showhighscore import ShowHighScore

_max_score_num = 10
_max_name_num = 8
class EntryHighScore(object):
    def __init__(self, score):
        self.new_score = score
        scores = []
        for line in open(CONFIG_DIR+"highscore.dat"):
            s, n, d = line.split()
            scores.append([float(s), n, float(d)])
        scores = scores[:_max_score_num]
        self.name = ["_"]*_max_name_num
        for i in range(_max_score_num):
            if self.new_score > scores[i][0]:
                scores = scores[:i] + [[self.new_score, self.make_name(), time.time()]] + scores[i:-1]
                break
        else:
            i = -1
        self.i = i
        self.scores = scores
        self.text = "Name: "

    def init(self):
        if self.i == -1:
            self.menu = MenuItems(["Final Score: %i"%self.new_score], BOX.Y/10)
        else:
            self.menu = MenuItems([self.text+"".join(self.name)], BOX.Y/10,
                                  title="High Score!")

    def save(self):
        if self.i > -1:
            f = open(CONFIG_DIR+"highscore.dat", "w")
            for s, n, d in self.scores:
                f.write("%i %s %f\n"%(s, n, d))
            f.close()

    def make_name(self, at=_max_name_num):
        name = "".join(self.name)
        return name[:at]

    def mainloop(self):
        if self.i == -1:
            self.show()
        else:
            self.entry()

    def entry(self):
        self.init()
        at = 0
        esc = 0
        while True:
            put = False
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in KS_ESC:
                        if at > 0:
                            at -= 1
                            self.name[at] = "_"
                            put = True
                        elif esc == 2:
                            return
                        else:
                            esc += 1
                            break
                    elif key in KS_RETURN and at > 0:
                        self.scores[self.i][1] = self.make_name(at)
                        self.save()
                        shs = ShowHighScore(self.scores, self.i)
                        shs.mainloop()
                        return
                    elif sdl2.SDLK_a <= key <= sdl2.SDLK_z:
                        if at < _max_name_num:
                            self.name[at] = chr(key - 32)
                            at += 1
                            put = True
                        esc = 0
                        break
                    elif sdl2.SDLK_0 <= key <= sdl2.SDLK_9:
                        if at < _max_name_num:
                            self.name[at] = str(key - sdl2.SDLK_0)
                            at += 1
                            put = True
                        esc = 0
                        break
            if put:
                self.menu.replace(0, self.text+"".join(self.name))
            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu.draw(focus=(1.0, 0.0, 0.0, 1.0))
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)

    def show(self):
        self.init()
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

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            self.menu.draw()
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
