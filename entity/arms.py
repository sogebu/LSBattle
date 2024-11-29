# coding: utf8
# entity/arms.py
from math import sqrt, sin, cos, pi

from go import Vector3, Vector4D, Lorentz
from go import hit_check
from model.pointsprite import PointSprite, PointSpriteDoppler
from model.flame import Flame
from program.box import BOX
from program.utils import DY_TEXTURE_KYU
from program import script


class Bullet(object):
    def __init__(self, X, U, L, N, S):
        self.X = X.copy()
        self.U = U.get_lis_glsl()
        self.L = L
        self.N = N.copy()
        self.S = S
        self.hit = False
        self.color = None

    def get_position(self, Xp):
        dX = self.X - Xp
        s = - dX.squared_norm() / (2.0 * self.N.inner_product(dX))
        return s

    def hit_check(self, X1, X0, collision_radius2, color=None):
        if not self.hit and X1.t > self.X.t:
            s = hit_check(self.X, self.N, self.S, X1, X0, collision_radius2)
            if s is not None:
                self.hit = True
                self.S = s
                self.color = color
                return True
            else:
                return False

    def draw(self, Xp, L, flame, vertex, U):
        s = self.get_position(Xp)
        if 0.0 < s < self.S:
            X = self.X.get_linear_add(self.N, s)
            vertex.extend(X.get_lis3())
            U.extend(self.U)
            return True
        elif self.hit:
            X = self.X.get_linear_add(self.N, self.S)
            return flame.draw(X, Xp, L, self.L)
        elif self.S < s:
            return False
        else:
            return True


class SlowBullet(object):
    def __init__(self, X, N, S, id):
        self.X = X.copy()
        self.N = N.copy()
        self.a = N.squared_norm()
        self.S = S
        self.id = id
        self.hit = False
        self.color = None

    def get_position(self, Xp):
        dX = Xp - self.X
        b = self.N.inner_product(dX)
        c = dX.squared_norm()
        s = (b + sqrt(b*b - self.a*c)) / self.a
        return s

    def hit_check(self, X1, X0, collision_radius2, color=None):
        if not self.hit and X1.t > self.X.t:
            s = hit_check(self.X, self.N, self.S, X1, X0, collision_radius2)
            if s is not None:
                self.hit = True
                self.S = s
                U = X1 - X0
                U /= -sqrt(-U.squared_norm())
                self.L = Lorentz(U)
                self.color = color
                return True
            else:
                return False

    def draw(self, Xp, L, flame, vertex, U):
        s = self.get_position(Xp)
        if 0.0 < s < self.S:
            X = self.X.get_linear_add(self.N, s)
            vertex.extend([X.x, X.y, X.z])
            U.extend([self.N.x, self.N.y, self.N.z, self.N.t])
            return True
        elif self.hit:
            X = self.X.get_linear_add(self.N, self.S)
            return flame.draw(X, Xp, L, self.L, color=self.color)
        elif self.S < s:
            return False
        else:
            return True


class _BaseBullets(object):
    def __iter__(self):
        return iter(self.bullets)


class Bullets(_BaseBullets):
    def __init__(self, world, color=(0.9, 0.1, 0.1, 0.8), psize=0.02):
        self.world = world
        self.bullets = []
        self.size = BOX.X * psize
        self.n = 0
        self.hit_n = 0
        self.model = PointSpriteDoppler(size=self.size, color=color, texture=DY_TEXTURE_KYU)
        self.color = [1.0 if i > 1.0 else i for i in Vector3(color[:3])*2.0] + [0.8]
        self.flame = Flame(S=0.3, v=0.4, psize=psize*2, color=self.color)

    def add(self, X, U, L, N, S):
        """
        L: background to player
        """
        self.bullets.append(Bullet(X, U, L, N, S))
        self.n += 1
        if len(self.bullets) > script.world.player_bullet_num_limit:
            self.bullets = self.bullets[-script.world.player_bullet_num_limit:]

    def hit_check(self, X1, X0, collision_radius, color=None):
        count = 0
        for bullet in self.bullets:
            if bullet.hit_check(X1, X0, collision_radius, color=color):
                count += 1
        return count

    def draw(self, Xp, L):
        if self.bullets:
            vertices = []
            U = []
            bullets = []
            for bullet in self.bullets:
                if bullet.draw(Xp, L, self.flame, vertices, U):
                    bullets.append(bullet)
                elif bullet.hit:
                    self.hit_n += 1
            self.bullets = bullets
            if vertices:
                self.model.draw(Xp, L, vertices=vertices, U=U)


class SlowBullets(_BaseBullets):
    def __init__(self, world, color=(0.9, 0.1, 0.1, 0.8), psize=0.02):
        self.world = world
        self.bullets = []
        self.size = BOX.X * psize
        self.n = 0
        self.hit_n = 0
        self.model = PointSpriteDoppler(size=self.size, color=color, texture=DY_TEXTURE_KYU)
        self.color = [1.0 if i > 1.0 else i for i in Vector3(color[:3])*2.0] + [0.4]
        self.flame = Flame(S=0.3, v=0.4, psize=psize*0.5, color=self.color)

    def add(self, X, N, S, id=None):
        self.bullets.append(SlowBullet(X, N, S, id))
        self.n += 1
        if len(self.bullets) > script.world.enemy_bullet_num_limit:
            self.bullets = self.bullets[-script.world.enemy_bullet_num_limit:]

    def hit_check(self, X1, X0, collision_radius, id=None, color=None):
        count = 0
        for bullet in self.bullets:
            if (id is None or id != bullet.id) and bullet.hit_check(X1, X0, collision_radius, color=color):
                count += 1
        return count

    def draw(self, Xp, L):
        if self.bullets:
            X = []
            U = []
            bullets = []
            for bullet in self.bullets:
                if bullet.draw(Xp, L, self.flame, X, U):
                    bullets.append(bullet)
                elif bullet.hit:
                    self.hit_n += 1
            self.bullets = bullets
            if X:
                self.model.draw(Xp, L, X, U)
