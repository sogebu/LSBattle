#coding: utf8
from math import sqrt, sin

from OpenGL import GL
import sdl2
import sdl2.ext

from entity import World
from program.const import *
from program.box import BOX
from program.utils import fill_screen, FramePerSec
from program.text import Sentence, drawSentence
from program import script
from sequence.locals import Keys
from sequence.stopmenu import StopMenu


class Play(object):
    WIN  = 0
    LOSE = 1
    ELSE = 2
    def __init__(self, level, scale, playerstate=None, total_score=0, item=None):
        BOX.resize(scale)
        self.stopmenu = StopMenu()
        self.level = level
        self.world = World(level, scale, playerstate, item)
        self.world.score += total_score

    def init(self):
        self.start_message = Sentence(self.level.stage_name, BOX.Y/10)
        self.clear_message = Sentence("STAGE CLEAR!", BOX.Y/8)
        self.gun_message = Sentence("Got New Gun!", BOX.Y/8)
        self.move_message = Sentence("Move,move!!", BOX.Y/5)
        self.keys = Keys()

        self.world.action(self.keys, 0.01)
        self.world.draw(self.keys)
        sdl2.SDL_GL_SwapWindow(BOX.window)

    def mainloop(self):
        self.init()
        scoreHight = BOX.Y/15
        textHeight = BOX.Y/25
        fps = FramePerSec()
        total_time = 0
        clear_time = 0
        lose_time = 0
        last_tick = sdl2.SDL_GetTicks()
        last_move = self.world.player.time
        shoot = False

        while True:
            ret = False
            for event in sdl2.ext.get_events():
                if event.type == sdl2.SDL_QUIT:
                    BOX.game_quit()
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key in KS_ESC:
                        sdl2.SDL_ShowCursor(1)
                        flg = self.stopmenu.mainloop()
                        sdl2.SDL_ShowCursor(0)
                        if flg == self.stopmenu.PLAY:
                            self.keys.load_config()
                            last_tick = sdl2.SDL_GetTicks()
                            break
                        elif flg == self.stopmenu.TITLE:
                            return self.ELSE
                    elif key == self.keys.accel_forward and self.level.enabled("accel_forward"):
                        self.keys.k_accel |= 1
                    elif key == self.keys.accel_back and self.level.enabled("accel_back"):
                        self.keys.k_accel |= 2
                    elif key == self.keys.accel_right and self.level.enabled("accel_right"):
                        self.keys.k_accel |= 4
                        self.keys.k_accel_priority = 0
                    elif key == self.keys.accel_left and self.level.enabled("accel_left"):
                        self.keys.k_accel |= 8
                        self.keys.k_accel_priority = 1
                    elif key == self.keys.turn_right and self.level.enabled("turn_right"):
                        self.keys.k_turn_right = True
                        self.keys.k_turn_priority1 = 0
                    elif key == self.keys.turn_left and self.level.enabled("turn_left"):
                        self.keys.k_turn_left  = True
                        self.keys.k_turn_priority1 = 1
                    elif key == self.keys.turn_up and self.level.enabled("turn_up"):
                        self.keys.k_turn_up = True
                        self.keys.k_turn_priority2 = 0
                    elif key == self.keys.turn_down and self.level.enabled("turn_down"):
                        self.keys.k_turn_down  = True
                        self.keys.k_turn_priority2 = 1
                    elif key == self.keys.shoot and self.level.enabled("shoot"):
                        shoot = True
                    elif key in KS_RETURN:
                        ret = True
                    elif key == self.keys.toggle_HUD and self.level.enabled("toggle_HUD"):
                        self.keys.k_map = (self.keys.k_map+1)%2
                    elif key == self.keys.change_gun and self.level.enabled("change_gun"):
                        self.world.player.state.gun_change()
                    elif key == self.keys.brake and self.level.enabled("brake"):
                        self.keys.k_brake = 1
                    elif key == self.keys.booster and self.level.enabled("booster"):
                        self.keys.k_booster = 1
                    elif script.game.cheat:
                        if key == sdl2.SDLK_c:
                            return self.WIN
                        elif key == sdl2.SDLK_x:
                            return self.LOSE
                elif event.type == sdl2.SDL_KEYUP:
                    key = event.key.keysym.sym
                    if key == self.keys.accel_forward:
                        if self.keys.k_accel&1 == 1:
                            self.keys.k_accel -= 1
                    elif key == self.keys.accel_back:
                        if self.keys.k_accel&2 == 2:
                            self.keys.k_accel -= 2
                    elif key == self.keys.booster:
                        self.keys.k_booster = 0
                    elif key == self.keys.accel_right:
                        if self.keys.k_accel&4 == 4:
                            self.keys.k_accel -= 4
                    elif key == self.keys.accel_left:
                        if self.keys.k_accel&8 == 8:
                            self.keys.k_accel -= 8
                    elif key == self.keys.brake:
                        self.keys.k_brake = 0
                    elif key == self.keys.turn_right:    self.keys.k_turn_right = False
                    elif key == self.keys.turn_left:     self.keys.k_turn_left  = False
                    elif key == self.keys.turn_up:       self.keys.k_turn_up    = False
                    elif key == self.keys.turn_down:     self.keys.k_turn_down  = False
                    elif key == self.keys.shoot:         shoot = False

            GL.glClear(GL.GL_DEPTH_BUFFER_BIT|GL.GL_COLOR_BUFFER_BIT)

            tick = sdl2.SDL_GetTicks()
            dt = tick - last_tick
            if dt == 0:
                dt = 1
            ds = dt * 0.001
            last_tick = tick
            fps.add(ds)
            total_time += ds

            if shoot:
                self.keys.k_bullet += dt
            else:
                if self.keys.k_bullet < 0:
                    self.keys.k_bullet += dt
                    if self.keys.k_bullet > 0:
                        self.keys.k_bullet = 0
                else:
                    self.keys.k_bullet = 0

            if self.keys.k_accel:
                last_move = self.world.player.time
                self.world.player.hit_flg = False

            if 0 < lose_time:
                self.keys.k_bullet = -1
            self.world.action(self.keys, ds)
            self.world.draw(self.keys)

            if self.world.player.gun_get_time + 1.5 > self.world.player.time:
                GL.glColor(1.0, 0.5, 0.5, 1.0)
                self.gun_message.draw_center()
            elif total_time < 2.0:
                GL.glColor(1.0, 0.0, 0.0, 1.0-total_time*0.5)
                self.start_message.draw_center()

            if clear_time == 0:
                if self.keys.k_accel == 0 and self.world.player.hit_flg:
                    s = self.world.player.time - last_move
                    if sin(s*4.0-2.0) < 0.8:
                        GL.glColor(1.0, 0.0, 0.0, 1.0)
                        self.move_message.draw_center()

            if self.world.enemies.check_death() and lose_time == 0:
                if clear_time == 0:
                    clear_time = total_time
                if ret or total_time - clear_time > 3.0:
                    return self.WIN
                else:
                    GL.glColor(1.0, 0.1, 0.1, 0.9)
                    self.clear_message.draw_center()
            elif self.world.player.state.hp <= 0:
                if lose_time == 0:
                    lose_time = total_time
                if ret or total_time - lose_time > self.world.player.delay + 2.0:
                    return self.LOSE
                else:
                    a = self.world.player.delay + 2.0 - total_time + lose_time
                    if a > 2.0:a = 2.0
                    fill_screen(0.0, 0.0, 0.0, 1.0-a/2.0)
            else:
                lose_time = 0

            if self.keys.k_map == 1:
                GL.glColor(0.3, 0.6, 0.3, 1.0)
                text = "Score %i\n"%self.world.score
                drawSentence(text, scoreHight, BOX.X*0.01, BOX.Y)

                g = self.world.player.P.U.get_gamma()
                u = sqrt(1.0 - 1.0/g**2)
                v = c * u
                text = "Stage: %i\n"%self.level.stage
                text += "FPS: %i\n"%(fps.get())
                text += "Speed: {:,d}m/s\n".format(int(v))
                text += "       %.3fc\n"%(u)
                text += "Lorentz factor: %.1f\n"%(g)
                text += "Enemy: %i"%(len([e for e in self.world.enemies if e.hp > 0]))
                GL.glColor(0.3, 0.6, 0.3, 1.0)
                drawSentence(text, textHeight, BOX.X*0.01, BOX.Y-scoreHight)

                text  = "Proper Time: %is\n"%(total_time)
                text += " World Time: %is\n"%(self.world.player.P.X.t)
                GL.glColor(1.0, 1.0, 1.0, 0.5)
                drawSentence(text, textHeight, BOX.X*0.01, BOX.Y-scoreHight-6*textHeight)

            sdl2.SDL_GL_SwapWindow(BOX.window)
