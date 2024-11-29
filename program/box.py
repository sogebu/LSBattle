# coding: utf8
# box.py
import os, sys

from OpenGL.GL import *
from OpenGL.GLU import *
import sdl2
import sdl2.ext

from program.const import VIEW_ANGLE, GAME_NAME, CONFIG_DIR, disp_sizes
from program import script


class _Box(object):
    def __init__(self):
        """
        Load setting file from CONFIG_DIR/setting.ini
        if loading is failed, do nothing
        """
        self.window = None
        self.context = None
        self.X = 800
        self.Y = 600
        self.FULL_SCREEN = False
        self.MODE = "EASY"
        self.SAVE = False
        try:
            for line in open(CONFIG_DIR+"setting.ini"):
                line = line.strip()
                w, v = line.split("=")
                if w == "DISPLAY_SIZE_X":
                    X = int(v)
                elif w == "DISPLAY_SIZE_Y":
                    Y = int(v)
                elif w == "FULL_SCREEN":
                    if v == "True":
                        FULL_SCREEN = True
                    else:
                        FULL_SCREEN = False
                elif w == "MODE":
                    if v == "EASY":
                        self.MODE = "EASY"
                    elif v == "NORMAL":
                        self.MODE = "NORMAL"
                    elif v == "HARD":
                        self.MODE = "HARD"
            if (X, Y) not in disp_sizes:
                X, Y = disp_sizes[0]
            self.X = X
            self.Y = Y
            self.FULL_SCREEN = FULL_SCREEN
        except:
            self.SAVE = True
            pass

    def game_init(self):
        if not sdl2.SDL_WasInit(sdl2.SDL_INIT_EVENTS) and self.window is None:
            sdl2.ext.init()
            w_mode = sdl2.SDL_DisplayMode()
            sdl2.SDL_GetCurrentDisplayMode(0, w_mode)
            if self.X > w_mode.w or self.Y > w_mode.h:
                self.X, self.Y = disp_sizes[0]
                self.SAVE = True
            flg = sdl2.SDL_WINDOW_OPENGL
            if self.FULL_SCREEN:
                flg |= sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
                self.X = w_mode.w
                self.Y = w_mode.h
                self.SAVE = True
            self.window = sdl2.SDL_CreateWindow(GAME_NAME,
                                                sdl2.SDL_WINDOWPOS_UNDEFINED,
                                                sdl2.SDL_WINDOWPOS_UNDEFINED,
                                                self.X, self.Y,
                                                flg)
            if not self.window:
                print((sdl2.SDL_GetError()))
                sdl2.ext.SDL_quit()
                sys.exit(-1)
            self.context = sdl2.SDL_GL_CreateContext(self.window)

            self.opengl_init()
            self.resize()

    def sdl2_quit(self):
        sdl2.SDL_GL_DeleteContext(self.context)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.ext.quit()
        self.window = None
        self.context = None

    def game_quit(self):
        self.save()
        self.sdl2_quit()
        sys.exit(0)

    def opengl_init(self):
        """
        setting some OpenGL parameter
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_CULL_FACE)
        glShadeModel(GL_SMOOTH)
        glPixelStorei(GL_PACK_ALIGNMENT, 4)

        # glFogfv(GL_FOG_COLOR, (1.0, 1.0, 1.0, 1.0))
        # glFogi(GL_FOG_MODE, GL_EXP)
        # glFogf(GL_FOG_START, 2)
        # glFogf(GL_FOG_END, 7)
        # glEnable(GL_FOG)

        glEnableClientState(GL_VERTEX_ARRAY)
        # glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SPRITE)

        glClearColor(*script.ui.backimage.color)

        # glEnable(GL_LINE_STIPPLE)
        # glLineStipple(4 , 0xAAAA)

    def resize(self, scale=1.0):
        """
        initialize opengl's matrix
        """
        glViewport(0, 0, self.X, self.Y)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(VIEW_ANGLE, self.X*1.0/self.Y, script.ui.near_clip*scale, script.ui.far_clip*scale)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.far_clip = script.ui.far_clip*scale

    def set_displaysize(self, i):
        if disp_sizes[i][0] != self.X and disp_sizes[i][1] != self.Y:
            self.X, self.Y = disp_sizes[i]
            self.FULL_SCREEN = False
            self.SAVE = True
            self.sdl2_quit()
            self.game_init()

    def set_fullscreen(self):
        if not self.FULL_SCREEN:
            self.FULL_SCREEN = True
            self.SAVE = True
            self.sdl2_quit()
            self.game_init()

    def set_mode(self, mode):
        self.MODE = mode
        self.SAVE = True

    def save(self):
        if self.SAVE:
            try:
                f = open(os.path.join(CONFIG_DIR, "setting.ini"), "w")
                f.write("DISPLAY_SIZE_X=%i\n"%self.X)
                f.write("DISPLAY_SIZE_Y=%i\n"%self.Y)
                if self.FULL_SCREEN:
                    f.write("FULL_SCREEN=True\n")
                else:
                    f.write("FULL_SCREEN=False\n")
                f.write("MODE=%s\n"%self.MODE)
                f.close()
            except:
                pass


BOX = _Box()
