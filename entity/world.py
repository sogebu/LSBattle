# coding: utf8
# entity/world.py
from math import pi
from random import random, randint

from OpenGL.GL import *

from go import Vector3, Vector4D, Matrix44, Lorentz
from entity import Player
from entity import Enemies
from entity import WireFrame
from entity import Sky
from entity import SolarSystem
from entity import Item
from program.const import *


class World(object):
    def __init__(self, level, scale, playerstate, item=None):
        self.level = level
        self.scale = scale
        self.playerstate = playerstate
        self.L = self.level.L * scale
        self.wireframe = WireFrame(scale=self.scale)
        self.sky = Sky()
        self.player = Player(world=self, level=level,
                             state=playerstate,
                             pos=Vector4D(0, 0, 0, self.L))
        self.solar = SolarSystem(self, self.player.P.X, self.scale)
        self.enemies = Enemies(world=self)
        self.item = None
        if not level.is_travel():
            self.init_set_enemy()
            self.init_set_item(item)
            self.init_set_worldline()
        self.score = 0

    def init_set_enemy(self):
        types = [randint(0, self.level.types - 1)for i in range(self.level.enemy_num-1)]
        types += [self.level.types-1]
        for typ in types:
            x = 6.0 * self.L * (2.0*random()-1.0)
            y = 6.0 * self.L * (2.0*random()-1.0)
            z = 6.0 * self.L * (1.0*random()-2.0)
            self.enemies.add(Vector4D(0, x, y, z), typ=typ, level=self.level)

    def init_set_item(self, item):
        if item is not None and item == self.playerstate.gun_num:
            pos = self.player.P.X + Vector4D(0, 0, 0.5, -5.0) * self.scale
            self.item = Item(item, pos, self.scale)

    def init_set_worldline(self):
        self.worldline_ref = {}
        lis = list(self.enemies) + [self.player]
        for a in lis:
            self.worldline_ref[id(a)] = a.worldline
            for b in lis:
                if a is b:
                    continue
                a.worldline.set_id(id(b.P.X))

    def action(self, keys, ds):
        n = int(ds * 10.0) + 1
        ds /= n
        count = 0
        while count < n:
            self.player.action(keys, ds)
            self.score += self.enemies.action(ds)
            self.solar.hit_check(self.player.P.X)
            self.item_action(ds)
            count += 1
        for wl in self.worldline_ref.values():
            wl.cut()

    def item_action(self, ds):
        if self.item is not None:
            self.item.action(ds)
            if self.item.check_collision(self.player.P.X, self.player.collision_radius2*4):
                self.player.state.gun_get()
                self.player.gun_get_time = self.player.time
                self.item = None

    def draw(self, keys):
        L = Lorentz(self.player.P.U)
        LL = Lorentz(-self.player.P.U)
        Xp = self.player.P.X
        matrix = self.player.quaternion.get_RotMat()
        if keys.k_look_behind:
            matrix *= Matrix44.y_rotation(pi)
        matrix_i = matrix.get_inverse_rot()

        glDisable(GL_DEPTH_TEST)
        glLoadMatrixd(matrix_i.to_opengl())
        self.sky.draw(matrix_i, LL)
        if keys.k_map:
            self.wireframe.draw(Xp, L)
        glEnable(GL_DEPTH_TEST)
        self.solar.draw(Xp, L, LL)
        self.enemies.draw(Xp, L, LL, self.worldline_ref)
        if self.item is not None:
            self.item.draw(Xp, L, LL)

        for gun in self.player.guns:
            gun.bullets.draw(Xp, L)
        self.enemies.bullets.draw(Xp, L)

        if keys.k_map:
            glDisable(GL_DEPTH_TEST)
            self.player.draw_window(L)
            glEnable(GL_DEPTH_TEST)
            self.player.draw_hp()
            self.player.draw_gun_name()
        self.player.draw_booster(keys)
