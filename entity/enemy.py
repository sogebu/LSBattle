# coding: utf8
# entity/enemy.py
import os
from random import random, randint
from math import sqrt, sin, cos, atan2, pi, isnan

from OpenGL.GL import *

from go import Vector3, Vector4D, Matrix44, Lorentz, Quaternion
from go import PhaseSpace, WorldLine
from go import calc_shoot_direction, calc_repulsion
from entity import SlowBullets
from model.polygon import Polygon
from model.flame import Flame
from program.const import IMG_DIR
from program.text import drawSentence3d
from program import script


class EnemyState(object):
    __slots__ = ("quaternion", "time", "hp")
    def __init__(self, quaternion, time, hp):
        self.quaternion = quaternion.copy()
        self.time = time
        self.hp = hp if hp > 0.0 else 0.0


class Enemy(object):
    def __init__(self, world, X, number, typ=None, level=None):
        self.world = world
        self.scale = world.scale
        self.number = number
        if typ is None:
            typ = min(randint(0, world.level.types-1), len(script.enemy.characters)-1)
        else:
            typ = min(typ, len(script.enemy.characters)-1)
        self.mode = script.enemy.characters[typ]
        self.size = self.mode.size * world.scale
        self.model = Polygon(os.path.join(IMG_DIR, self.mode.name),
                             func=lambda x,y,z:(x*self.size, y*self.size, z*self.size),
                             color=self.mode.color)

        self.resistivity = self.mode.resistivity
        self.repulsion = script.enemy.repulsion
        self.repulsion_player = (script.enemy.repulsion + script.player.repulsion) * 0.5
        self.max_hp = self.mode.hp
        self.hp = self.max_hp
        self.bullet_range = self.mode.bullet_range * world.scale
        self.shoot_div = self.mode.shoot_div
        self.shoot_div_phi = self.mode.shoot_div_phi
        if len(self.shoot_div):
            self.shoot = self._shoot_n
        else:
            self.shoot = self._shoot
        self.collision_radius  = self.mode.collision_radius * self.size
        self.collision_radius2 = self.collision_radius**2.0
        self.collision_radius_by_friend  = self.mode.collision_radius_by_friend * self.size
        self.collision_radius_by_friend2 = self.collision_radius_by_friend**2.0
        self.flame = Flame(S=script.enemy.flame.life*self.size, v=script.enemy.flame.speed,
                           n=script.enemy.flame.num, m=script.enemy.flame.num*2,
                           color=script.enemy.flame.color, psize=script.enemy.flame.size*self.size)

        self.quaternion = Quaternion()
        # Puts time coordinate slightly past behind the PLC of player.
        self.P = PhaseSpace(X, Vector4D(1,0,0,0))
        self.P.X.t = -X.distance_to(world.player.P.X) - 1.0
        state = EnemyState(self.quaternion, self.P.X.t, self.hp)
        self.worldline = WorldLine(self.P, state)
        self.P.X.t = -X.distance_to(world.player.P.X) + 0.1 * world.scale
        state = EnemyState(self.quaternion, self.P.X.t, self.hp)
        self.worldline.add(self.P, state)

        r = sqrt(self.mode.think.near_n**2 + self.mode.think.near_p**2)
        if r > 1.0:
            self.mode.think.near_n *= self.mode.acceleration / r
            self.mode.think.near_p *= self.mode.acceleration / r
        else:
            self.mode.think.near_n *= self.mode.acceleration
            self.mode.think.near_p *= self.mode.acceleration
        r = sqrt(self.mode.think.far_n**2 + self.mode.think.far_p**2)
        if r > 1.0:
            self.mode.think.far_n *= self.mode.acceleration / r
            self.mode.think.far_p *= self.mode.acceleration / r
        else:
            self.mode.think.far_n *= self.mode.acceleration
            self.mode.think.far_p *= self.mode.acceleration

        self.time = -self.P.X.distance_to(world.player.P.X)
        if level is not None:
            if level.is_easy():
                self.mode.shoot_interval *= 3.0
            elif level.is_normal():
                self.mode.shoot_interval *= 2.0
        self.next_shoot_time = self.time + self.mode.shoot_interval
        self.change_time = self.time + self.mode.think.zgzg_interval
        self.zgzg = randint(0, 3)
        self.distance0 = ((self.mode.think.distance0 + random()) * self.size)**2
        self.distance1 = ((self.mode.think.distance1 + random()) * self.size)**2
        self.omega_max = 1.0/self.size

        self.X_to_head = None
        self.X_dead = None
        self.last_R = None

        self.i = id(self.P.X)

    def _shoot(self, forward):
        n = Vector4D(1.0/self.mode.bullet_speed, forward)
        Lorentz(-self.P.U).transform(n)
        self.world.enemies.bullets.add(self.P.X, n, self.bullet_range, self.number)

    def _shoot_n(self, forward):
        n = Vector4D(1.0/self.mode.bullet_speed, forward)
        L = Lorentz(-self.P.U)
        L.transform(n)
        self.world.enemies.bullets.add(self.P.X, n, self.bullet_range, self.number)
        up = self.quaternion.get_upward_lis3_i()
        for i in range(len(self.shoot_div)):
            div = self.shoot_div[i]
            m = Quaternion.from_ax((i+1)*self.shoot_div_phi, up).get_RotMat()
            d = m.get_rotate(forward)
            for j in range(div):
                mm = Quaternion.from_ax(2*pi*j/div, forward).get_RotMat()
                dd = Vector4D(1.0/self.mode.bullet_speed, mm.get_rotate(d))
                L.transform(dd)
                self.world.enemies.bullets.add(self.P.X, dd, self.bullet_range, self.number)

    def check_shoot(self):
        if self.next_shoot_time < self.time:
            self.next_shoot_time = self.time + self.mode.shoot_interval + (0.5 - random())*0.5
            forward = Vector3(self.quaternion.get_forward_lis3_i())
            self.shoot(forward)

    def think(self, acceleration):
        if self.change_time < self.time:
            self.change_time += self.mode.think.zgzg_interval
            self.zgzg = randint(0, 3)

        r = self.P.X.distance_to_squared(self.X_to_head)
        if r < self.distance0:
            nn = self.mode.think.near_n
            pp = self.mode.think.near_p
        elif r < self.distance1:
            nn = self.mode.think.far_n
            pp = self.mode.think.far_p
        else:
            nn = abs(self.mode.think.far_n)
            pp = self.mode.think.far_p

        n = (self.X_to_head - self.P.X).d
        n.normalize(nn)
        if pp:
            if self.zgzg < 2: p = Vector3(self.quaternion.get_upward_lis3_i())
            else:             p = Vector3(self.quaternion.get_right_lis3_i())
            if self.zgzg%2:   p *= pp
            else:             p *= -pp
            n += p
        acceleration.d += n

    def hit_check(self, X1, X0, color=None):
        score = 0
        damage = self.world.player.bullet_hit_check(X1, X0, self.collision_radius2)
        if damage:
            if self.hp < damage:
                s = script.game.score.hit * self.hp
            else:
                s = script.game.score.hit * damage
            self.hp -= damage
            score += s

        damage = self.world.enemies.bullets.hit_check(X1, X0, self.collision_radius_by_friend2, self.number)
        if damage:
            self.hp -= damage
            s = script.game.score.hit_by_friend * damage
            score += s
        return score

    def calc_repulsion(self, acceleration):
        for enemy in self.world.enemies:
            if enemy is self:
                continue
            X1, U1 = enemy.worldline.get_XU_on_PLC(self.P.X)
            if X1 is not None:
                calc_repulsion(self.P.X, X1, U1,
                               self.collision_radius + enemy.collision_radius,
                               self.repulsion,
                               acceleration)

        X1, U1 = self.world.player.worldline.get_XU_on_PLC(self.P.X)
        if X1 is not None:
            calc_repulsion(self.P.X, X1, U1,
                           self.collision_radius + self.world.player.collision_radius,
                           self.world.player.repulsion,
                           acceleration)

        self.world.solar.calc_repulsion(self.P.X, acceleration,
                                        self.collision_radius,
                                        self.repulsion*100.0)

    def change_direction(self, X_playerPLC, U_playerPLC, ds):
        forward = Vector3(self.quaternion.get_forward_lis3_i())
        direction = calc_shoot_direction(self.P.X, self.P.U,
                                         X_playerPLC, U_playerPLC,
                                         self.mode.bullet_speed)
        if direction is None:
            direction = calc_shoot_direction(self.P.X, self.P.U,
                                             X_playerPLC, U_playerPLC,
                                             1.0)
        direction = Vector3(direction)
        ax = forward.cross(direction)
        ax_length = ax.length()
        if ax_length > 0.0:
            c = forward.dot(direction)
            cmin = cos(self.omega_max * ds)
            if c < cmin:
                c = cmin
            c2 = sqrt(abs(c + 1.0)*0.5)
            s2 = sqrt(abs(1.0 - c2*c2))
            ax *= s2 / ax_length
            q = Quaternion(c2, ax)
            self.quaternion = q * self.quaternion

    def action(self, ds):
        assert(self.i == id(self.P.X))
        Xp = self.world.player.P.X
        score = 0
        self.X_to_head = self.world.player.worldline.get_X_FP(self.P.X, random())
        if self.hp <= 0.0 or Xp.t <= self.P.X.t or Xp.squared_norm_to(self.P.X) >= 0.0:
            return 0, False
        X_playerPLC, U_playerPLC = self.world.player.worldline.get_XU_on_PLC(self.P.X)
        if self.X_to_head is None:
            self.X_to_head = Vector4D(0, 0, 0, self.world.L*0.7)
            X_playerPLC = Vector4D(0, 0, 0, self.world.L*0.7)
            U_playerPLC = Vector4D(1, 0, 0, 0)

        acceleration = self.P.get_resist(self.resistivity)
        self.calc_repulsion(acceleration)
        self.think(acceleration)
        self.P.transform(acceleration, ds)
        self.time += ds

        self.check_shoot()

        self.change_direction(X_playerPLC, U_playerPLC, ds)

        X1 = self.P.X
        X0 = self.worldline.get_last()
        score += self.hit_check(X1, X0)

        state = EnemyState(self.quaternion, self.time, self.hp)
        self.worldline.add(self.P, state)

        if self.hp <= 0.0:
            if self.X_dead is None:
                self.X_dead = self.P.X.copy()
                self.L_dead = Lorentz(-self.P.U)
                s = script.game.score.break_enemy
                score += s

        if self.hp > 0.0 and Xp.t > self.P.X.t and Xp.squared_norm_to(self.P.X) < 0.0:
            return score, True
        else:
            return score, False

    def draw_timer(self, LX, R, R_i, state0, state1, s):
        text = script.enemy.timer.format%((1.0-s)*state0.time + s*state1.time)
        glColor(*script.enemy.timer.color)
        X = LX + Vector4D(0.0, R_i.up) * self.size
        drawSentence3d(text, script.enemy.timer.size*self.size, X, R)

    def draw_hpbar(self, LX, R_i, state0, state1, s):
        hp = (1.0-s)*state0.hp + s*state1.hp

        right = Vector3(R_i.right)
        O = LX.d - right*(script.enemy.hpbar.position*self.size)
        dr = right*(script.enemy.hpbar.width*self.scale*self.max_hp**0.1)

        dup = Vector3(R_i.up)
        O -= dup * (self.size*0.5)
        perHP = script.enemy.hpbar.length_parhp * self.scale * self.max_hp**-0.1
        glBegin(GL_QUADS)
        if hp < self.max_hp:
            l = perHP * hp
            glColor(*script.enemy.hpbar.back_color)
            glVertex(*(O + dup*l))
            glVertex(*(O + dup*l + dr))
            l = perHP * self.max_hp
            glVertex(*(O + dup*l + dr))
            glVertex(*(O + dup*l))
        l = perHP * hp
        glColor(*script.enemy.hpbar.bar_color)
        glVertex(*O)
        glVertex(*(O + dr))
        glVertex(*(O + dup*l + dr))
        glVertex(*(O + dup*l))
        glEnd()

    def draw(self, Xp, L, LL):
        X, U = self.worldline.get_XU_on_PLC(Xp)
        if X is not None: # If enemy is not dead...
            state0, state1, s = self.worldline.get_State_on_PLC(Xp)
            q = state0.quaternion.get_spherep(state1.quaternion, s)
            R = q.get_RotMat()
            self.last_R = R
            self.model.draw(Xp, L, LL, X, U, R) # draw body's polygon

            LX = L.get_transform(X-Xp)
            R_i = R.get_inverse_rot()
            glDisable(GL_CULL_FACE)
            if script.enemy.timer.visible:
                self.draw_timer(LX, R, R_i, state0, state1, s)
            if script.enemy.hpbar.visible:
                self.draw_hpbar(LX, R_i, state0, state1, s)
            glEnable(GL_CULL_FACE)

            return True

        if self.hp <= 0.0: # enemy is dead...
            return self.flame.draw(self.X_dead, Xp, L, self.L_dead)


class Enemies(object):
    def __init__(self, world):
        self.enemies = []
        self.n = 0
        self.world = world
        self.scale = world.scale
        self.bullets = SlowBullets(world,
                                   psize=script.enemy.bullet.size,
                                   color=script.enemy.bullet.color)

    def __iter__(self):
        return iter(self.enemies)

    def add(self, x, typ=None, level=None):
        self.enemies.append(Enemy(self.world, x, self.n, typ=typ, level=level))
        self.n += 1

    def action(self, ds):
        actor = sorted(self.enemies, key=lambda enemy:enemy.P.X.t)
        score = 0
        while actor:
            tmp = []
            for enemy in actor:
                s, flg = enemy.action(ds)
                score += s
                if flg:
                    tmp.append(enemy)
            actor = sorted(tmp, key=lambda enemy:enemy.P.X.t)
        return score

    def check_death(self):
        return all(enemy.hp <= 0.0 for enemy in self.enemies)

    def draw(self, Xp, L, LL, ref):
        enemies = []
        for enemy in self.enemies:
            if enemy.draw(Xp, L, LL) or enemy.hp > 0.0:
                enemies.append(enemy)
            else:
                del ref[id(enemy)]
                for wl in ref.values():
                    wl.del_id(id(enemy.P.X))
        self.enemies = enemies

    def hit_check(self, X1, X0, collision_radius2, color=None):
        return self.bullets.hit_check(X1, X0, collision_radius2, color=color)
