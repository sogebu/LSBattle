#coding: utf8
from datetime import date

from OpenGL import GL

from program.const import *
from program.box import BOX
from sequence.locals import MenuItems, M

_rank = ["1st",
         "2nd",
         "3rd",
         "4th",
         "5th",
         "6th",
         "7th",
         "8th",
         "9th",
         "10th"]

class ShowHighScore(object):
    def __init__(self, scores, i):
        self.make_text(scores)
        self.i = i
        self.resetable = False

    def make_text(self, scores):
        self.texts = []
        for n, (score, name, d) in enumerate(scores):
            d = date.fromtimestamp(d)
            self.texts.append("%4s %8.0f  %10s  %4i-%2i-%2i"%(_rank[n], score, name, d.year, d.month, d.day))

    @classmethod
    def ranking(self):
        scores = []
        for line in open(CONFIG_DIR+"highscore.dat"):
            s, n, d = line.split()
            scores.append([float(s), n, float(d)])
        shs = ShowHighScore(scores, -1)
        shs.resetable = True
        return shs

    def reset(self):
        scores = [[0, "A", 0.0]for i in range(10)]
        f = open(CONFIG_DIR+"highscore.dat", "w")
        for s, n, d in scores:
            f.write("%i %s %f\n"%(s, n, d))
        f.close()
        self.make_text(scores)
        self.init()

    def init(self):
        if self.resetable:
            self.menu = MenuItems(self.texts+["Reset highscores"], BOX.Y/20, ret=True, title="Ranking", row=M.BOTTOM)
        else:
            self.menu = MenuItems(self.texts, BOX.Y/18, ret=False, title="Ranking", row=M.BOTTOM)
        self.menu.choice = self.i

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
                    elif self.resetable and key == sdl2.SDLK_UP:
                        self.menu.up()
                    elif self.resetable and key == sdl2.SDLK_DOWN:
                        self.menu.down()
                    elif key in KS_RETURN:
                        if self.resetable:
                            choice = self.menu.choice
                            break
                        else:
                            return
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse = event.button
                    if mouse.button == 1:
                        choice = self.menu.mouse_check(mouse.x, mouse.y)
                        break

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            if self.resetable and choice >= 0 and self.resetable:
                if choice == self.menu.RETURN:
                    return
                elif choice == self.menu.RETURN-1:
                    self.reset()
            self.menu.draw(focus=(1.0, 0.0, 0.0, 1.0))
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
