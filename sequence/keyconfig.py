#coding: utf8
from OpenGL import GL
import sdl2
import sdl2.ext

from program.const import *
from program.box import BOX
from sequence.locals import Keys, MenuItems, M


class KeyConfig(object):

    def init(self):
        self.keys = Keys()
        self.keys.load_map()
        self.menu_1 = MenuItems(self.keys.name2+["default"], BOX.Y/22, 0.15,
                                colum=M.LEFT_RIGHT, row=M.BOTTOM, ofy=BOX.Y/15,
                                ret=True, title="Key Config")
        self.menu_1.repos_colum(self.menu_1.RETURN-1, M.CENTER)
        self.change_menu_2()

    def change_menu_2(self):
        texts_2 = []
        for name, key in self.keys:
            texts_2.append(self.keys.key_map[key])
        texts_2 += [""]
        self.menu_2 = MenuItems(texts_2, BOX.Y/22, 0.15,
                                colum=M.RIGHT_LEFT, row=M.BOTTOM, ofy=BOX.Y/15,
                                ret=True)
        self.menu_2.choice = self.menu_1.choice

    def mainloop(self):
        self.init()
        mode = 1
        while True:

            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if mode == 1:
                        if key in KS_ESC:
                            return
                        elif key == sdl2.SDLK_UP:
                            self.menu_1.up()
                            self.menu_2.up()
                        elif key == sdl2.SDLK_DOWN:
                            self.menu_1.down()
                            self.menu_2.down()
                        elif key in KS_RETURN:
                            if self.menu_1.choice == self.menu_1.RETURN:
                                self.keys.save()
                                return
                            elif self.menu_1.choice == self.menu_1.RETURN-1:
                                self.keys.default()
                                self.change_menu_2()
                            else:
                                mode = 2
                        elif key == sdl2.SDLK_RIGHT and self.menu_1.choice < self.menu_1.RETURN-1:
                            mode = 2
                    elif mode == 2:
                        if key in self.keys.key_map:
                            name = self.keys.names[self.menu_1.choice]
                            setattr(self.keys, name, key)
                            self.menu_2.replace(self.menu_1.choice, self.keys.key_map[key])
                            mode = 1
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse = event.button
                    if mouse.button == 1:
                        choice = self.menu_1.mouse_check(mouse.x, mouse.y)
                        if 0 <= choice:
                            if choice == self.menu_1.RETURN:
                                self.keys.save()
                                return
                            elif choice == self.menu_1.RETURN-1:
                                mode = 1
                                self.keys.default()
                                self.change_menu_2()
                            else:
                                mode = 2
                                self.menu_2.choice = self.menu_1.choice
                        else:
                            choice = self.menu_2.mouse_check(mouse.x, mouse.y)
                            if 0 <= choice < self.menu_2.RETURN-1:
                                self.menu_1.choice = self.menu_2.choice
                                mode = 2

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)
            if self.menu_1.choice == self.menu_1.RETURN:
                focus_1 = focus_2 = None
            elif mode == 1:
                focus_1 = None
                focus_2 = (1.0, 1.0, 1.0, 1.0)
            elif mode == 2:
                focus_2 = None
                focus_1 = (1.0, 1.0, 1.0, 1.0)
            self.menu_1.draw(focus_1)
            self.menu_2.draw(focus_2)
            sdl2.SDL_GL_SwapWindow(BOX.window)
            sdl2.SDL_Delay(10)
