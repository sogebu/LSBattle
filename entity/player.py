# coding: utf8
# entity.player.py
from math import pi

from OpenGL.GL import *

from go import Vector3, Vector4D, Matrix44, Lorentz, Quaternion
from go import PhaseSpace, WorldLine
from go import calc_repulsion
from entity import Bullets
from model.pointsprite import PointSprite
from model.lines import Lines
from program.box import BOX
from program.utils import FlatScreen, fill_screen, DY_TEXTURE_EDGE
from program.text import drawSentence
from program import script


class PlayerState(object):
    def __init__(self):
        self.max_gun_num = len(script.player.gun)
        self.gun_mode = 0
        self.gun_num = 1
        self.make_gun_icon()
        self.reset_hp()

    def reset_hp(self):
        self.hp = script.player.hp
    
    def make_gun_icon(self):
        gun = script.player.gun[self.gun_mode]
        self.gun_info = script.player.gun_info.format%{
                "MODE":self.gun_mode+1,
                "NUM":self.gun_num,
                "MAX":self.max_gun_num,
                "NAME":gun.name,
                "POWER":gun.power,
                "RANGE":gun.range,
                "RELOAD_TIME":gun.reload_time,
                "ACTION":("Automatic" if gun.automatic else "Single")
            }
    
    def gun_change(self):
        self.gun_mode = (self.gun_mode+1)%self.gun_num
        self.make_gun_icon()

    def gun_get(self):
        if self.gun_num < self.max_gun_num:
            self.gun_num += 1
        self.gun_mode = self.gun_num - 1
        self.make_gun_icon()

class Gun(object):
    def __init__(self, world, gun_data):
        self.world = world
        self.name = gun_data.name
        self.bullets = Bullets(world, color=gun_data.bullet.color,
                                      psize=gun_data.bullet.size*world.scale)
        self.speed = gun_data.speed
        self.range = gun_data.range * world.scale
        self.reload_time = gun_data.reload_time
        self.power = gun_data.power
        if gun_data.automatic:
            self.gun_action = self._gun_action_automatic
        else:
            self._gun_flg = True
            self.gun_action = self._gun_action_single
        self.shoot_position = gun_data.shoot_position * self.world.scale
        self.div = gun_data.div

    def _shoot(self, ds, par_frame):
        player = self.world.player
        L = Lorentz(-player.P.U)
        LL = Lorentz(player.P.U)
        matrix = player.quaternion.get_RotMat()
        X = player.P.X.copy()
        X += Vector4D.from_tv(0.0, matrix.up) * self.shoot_position
        v = -Vector3(matrix.forward)
        n = Vector4D.from_tv(1.0, v)
        L.transform(n)
        right = matrix.right
        self.bullets.add(X, LL, n, self.range)
        nlis = []
        for i in xrange(len(self.div)):
            m = Quaternion.from_ax((i+1)*pi/30, right).get_RotMat()
            d = m.get_rotate(v)
            div = self.div[i]
            for j in xrange(div):
                mm = Quaternion.from_ax(2*pi*j/div, v).get_RotMat()
                n = Vector4D.from_tv(1.0, mm.get_rotate(d))
                L.transform(n)
                nlis.append(n)
                self.bullets.add(X, LL, n, self.range)

        dt = ds / par_frame
        for i in xrange(1, par_frame):
            XX = X.get_linear_add(player.P.U, dt*i)
            self.bullets.add(XX, LL, n, self.range)
            for nn in nlis:
                self.bullets.add(XX, LL, nn, self.range)

    def _gun_action_single(self, keys, ds):
        if self._gun_flg:
            if keys.k_bullet > 0:
                self._shoot(ds, 1)
                self._gun_flg = False
                keys.k_bullet -= self.reload_time
        else:
            if keys.k_bullet == 0:
                self._gun_flg = True

    def _gun_action_automatic(self, keys, ds):
        if keys.k_bullet > 0:
            par_frame = int(ds*1000/self.reload_time) + 1
            self._shoot(ds, par_frame)
            keys.k_bullet -= self.reload_time * par_frame

class Player(object):

    def __init__(self, world, state, pos):
        self.world = world
        self.state = state
        self.P = PhaseSpace(pos, Vector4D(1,0,0,0))
        self.time = 0.0
        self.recovery_interval = script.player.recovery_interval
        self.recovery_time = self.time + self.recovery_interval
        self.quaternion = Quaternion()
        start = self.P.copy()
        start.X.t = 0.0
        self.worldline = WorldLine(start)
        self.worldline.add(self.P)

        self.maxhp = script.player.hp
        self.hp_times = []
        self.bloot_time = self.time - 1.0
        self.acceleration = script.player.acceleration
        self.resistivity = script.player.resistivity
        self.turn_speed_1 = 0.0
        self.turn_speed_2 = 0.0
        self.turn_acceleration = script.player.turn_acceleration
        self.turn_resistivity = script.player.turn_resistivity
        self.collision_radius = script.player.collision_radius*world.scale
        self.collision_radius2 = (script.player.collision_radius*world.scale)**2
        self.delay = self.collision_radius
        self.repulsion = (script.player.repulsion + script.enemy.repulsion) * 0.5

        self.guns = [Gun(self.world, g) for g in script.player.gun]
        self.gun_get_time = -10.0

        self.hit_flg = False

        if script.player.window.texture is None:
            tex = DY_TEXTURE_EDGE
        else:
            tex = script.player.window.texture
        self.on_position = PointSprite(color=script.player.window.color,
                                       size=BOX.Y*script.player.window.size,
                                       size_w=False,
                                       texture=tex)
        r, g, b, a = script.player.window.pre_color
        self.lines = Lines([r, g, b, a/2])

    def get_acceleration(self, keys, ds, acceleration):
        accel = keys.k_accel
        matrix = self.quaternion.get_RotMat()
        if accel&1:
            ac = -Vector4D.from_tv(0.0, matrix.forward)
        elif accel&2:
            ac = Vector4D.from_tv(0.0, matrix.forward)
        else:
            ac = Vector4D()

        if keys.k_accel_priority == 0:
            if accel&4:
                ac += Vector4D.from_tv(0.0, matrix.right)
            elif accel&8:
                ac -= Vector4D.from_tv(0.0, matrix.right)
        else:
            if accel&8:
                ac -= Vector4D.from_tv(0.0, matrix.right)
            elif accel&4:
                ac += Vector4D.from_tv(0.0, matrix.right)

        if keys.k_booster:
            ac.normalize(self.acceleration * script.player.turbo)
        else:
            ac.normalize(self.acceleration)

        acceleration += ac

    def calc_repulsion(self, acceleration):
        for enemy in self.world.enemies:
            X1, U1 = enemy.worldline.get_XU_on_PLC(self.P.X)
            if X1 is not None:
                calc_repulsion(self.P.X, X1, U1,
                               self.collision_radius + enemy.collision_radius,
                               self.repulsion,
                               acceleration)
        U = Vector4D(1.0, 0.0, 0.0, 0.0)
        for star in self.world.stars.stars:
            star.X.t = self.P.X.t - self.P.X.distance_to(star.X)
            calc_repulsion(self.P.X, star.X, U,
                           self.collision_radius*0.3+star.radius,
                           self.repulsion*1000,
                           acceleration)

    def change_direction(self, keys, ds):
        if keys.k_turn_priority1 == 0:
            if keys.k_turn_right:
                self.turn_speed_1 += self.turn_acceleration * ds
            elif keys.k_turn_left:
                self.turn_speed_1 -= self.turn_acceleration * ds
        else:
            if keys.k_turn_left:
                self.turn_speed_1 -= self.turn_acceleration * ds
            elif keys.k_turn_right:
                self.turn_speed_1 += self.turn_acceleration * ds
        if keys.k_turn_priority2 == 0:
            if keys.k_turn_up:
                self.turn_speed_2 -= self.turn_acceleration * ds
            elif keys.k_turn_down:
                self.turn_speed_2 += self.turn_acceleration * ds
        else:
            if keys.k_turn_down:
                self.turn_speed_2 += self.turn_acceleration * ds
            elif keys.k_turn_up:
                self.turn_speed_2 -= self.turn_acceleration * ds
        matrix = self.quaternion.get_RotMat()
        self.quaternion *= Quaternion.from_ax(self.turn_speed_1 * ds, matrix.up)
        self.quaternion *= Quaternion.from_ax(self.turn_speed_2 * ds, matrix.right)
        self.turn_speed_1 -= self.turn_resistivity * self.turn_speed_1 * ds
        self.turn_speed_2 -= self.turn_resistivity * self.turn_speed_2 * ds

    def action(self, keys, ds):
        self.change_direction(keys, ds)

        self.guns[self.state.gun_mode].gun_action(keys, ds)

        if keys.k_brake:
            acceleration = self.P.get_resist(self.resistivity*30)
        else:
            acceleration = self.P.get_resist(self.resistivity)
        self.get_acceleration(keys, ds, acceleration)
        self.calc_repulsion(acceleration)
        self.P.transform(acceleration, ds)
        self.time += ds

        X1 = self.P.X
        X0 = self.worldline.get_last()
        if self.world.enemies.hit_check(X1, X0, self.collision_radius2, color=(0.95, 0.1, 0.1, 0.8)):
            self.hp_times.append(self.time + self.delay - 0.03)
            self.bloot_time = self.time + self.delay

        self.worldline.add(self.P)

        times = []
        for t in self.hp_times:
            if t < self.time:
                self.state.hp -= 1
                self.hit_flg = True
            else:
                times.append(t)
        self.hp_times = times

        if self.time > self.recovery_time:
            if self.state.hp < script.player.hp:
                self.state.hp += 1
                self.recovery_time = self.time + self.recovery_interval
            else:
                self.recovery_time = self.time + self.recovery_interval*0.1

    def draw_hp(self):
        FlatScreen.push()
        ox = BOX.X * script.player.hpbar.position_x
        oy = BOX.Y * script.player.hpbar.position_y
        lx = BOX.X * script.player.hpbar.length_x
        ly = BOX.Y * script.player.hpbar.length_y
        glBegin(GL_QUADS)
        if self.state.hp < self.maxhp:
            glColor(*script.player.hpbar.back_color)
            glVertex(ox,    oy)
            glVertex(ox+lx, oy)
            glVertex(ox+lx, oy+ly)
            glVertex(ox,    oy+ly)
        lh = lx * self.state.hp * 1.0 / self.maxhp
        dt = (self.time - self.bloot_time) / script.player.hpbar.blood_time
        r, g, b, a = script.player.hpbar.color
        if 0.0 < dt < 1.0:
            br, bg, bb, ba = script.player.hpbar.blood_color
            ba *= 1.0 - dt
            glColor(r, g, b, a*(1.0-dt))
            r = r*(1.0 - ba) + br*ba
            g = g*(1.0 - ba) + bg*ba
            b = b*(1.0 - ba) + bb*ba
        glColor(r, g, b, a)
        glVertex(ox,    oy)
        glVertex(ox+lh, oy)
        glVertex(ox+lh, oy+ly)
        glVertex(ox,    oy+ly)
        glEnd()
        FlatScreen.pop()

    def draw_gun_name(self):
        text = self.state.gun_info
        glColor(*script.player.gun_info.color)
        drawSentence(text, BOX.Y * script.player.gun_info.height,
                           BOX.X * script.player.gun_info.position_x,
                           BOX.Y * script.player.gun_info.position_y)

    def draw_booster(self, keys):
        if keys.k_booster:
            glColor(1.0, 1.0, 1.0, 1.0)
            drawSentence("Booster on!", BOX.Y*0.08, BOX.X*0.01, BOX.Y*0.1)

    def bullet_hit_check(self, X1, X0, collision_radius2):
        damege = 0
        for i in xrange(self.state.gun_num):
            gun = self.guns[i]
            damege += gun.bullets.hit_check(X1, X0, collision_radius2) * gun.power
        return damege

    def draw_window(self, L):
        vertices_p = []
        vertices_f = []
        for enemy in self.world.enemies:
            X_PLC = enemy.worldline.get_X_FP(self.P.X, 0.0)
            if X_PLC is not None:
                vertices_p.extend(X_PLC.get_lis3())
                X_FLC = enemy.worldline.get_X_FP(self.P.X, 1.0)
                vertices_f.extend(X_FLC.get_lis3())
        if vertices_p:
            self.on_position.draw(self.P.X, L, vertices_p)
            self.on_position.draw(self.P.X, L, vertices_f,
                                  size=BOX.Y*script.player.window.pre_size,
                                  color=script.player.window.pre_color)
            glLineWidth(5)
            self.lines.draw(self.P.X, L, vertices_p, vertices_f)
            glLineWidth(1)

    def draw_lines(self, L, m):
        # glLineWidth(1)
        a = 0.01
        b = 0.0
        drawrange = 100
        earth_drawrange = 10
        ox, oy, oz = m.forward
        ox *= a
        oy *= a
        oz *= a

        # Draw a lint to the earth.
        glBegin(GL_LINES)
        x, y, z = L.get_transform_lis3(self.world.stars.stars[0].X - self.P.X)
        glColor(0.0, 0.0, 1.0, 0.5)
        r2 = (x - ox)**2.0 + (y - oy)**2.0 + (z - oz)**2.0
        if r2>earth_drawrange:
            c = b / sqrt(r2)
            glVertex(ox+(x-ox)*c, oy+(y-oy)*c, oz+(z-oz)*c)
            glVertex(x, y, z)

        # # Draw a line to the enemies.
        # glColor(1.0, 0.0, 0.0, 0.5)
        # for enemy in self.world.enemies:
        #     x, y, z = L.get_transform_lis3(enemy.P.X-self.P.X)
        #     r2 = (x - ox)**2.0 + (y - oy)**2.0 + (z - oz)**2.0
        #     if r2>drawrange:
        #         c = b / sqrt(r2)
        #         glVertex(ox+(x-ox)*c, oy+(y-oy)*c, oz+(z-oz)*c)
        #         glVertex(x, y, z)
        glEnd()
