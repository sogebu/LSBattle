# coding: utf8
# entity/star.py
from math import pi

from OpenGL.GL import *

from go import Matrix44, Vector4D, Lorentz
from model.polygon import Polygon
from program.const import IMG_DIR, c
from program.box import BOX
from program.text import drawSentence3d


_data = [["earth.jpg", 6378000, 23.4*pi/180,            0],
         ["moon.jpg",  1738000,           0,    384400000],
         ["sun.gif", 695500000,           0, 149597870700]]

def _high_func(sphere_radius, phi, rescale):
    mat = Matrix44.scale(sphere_radius*rescale) * Matrix44.x_rotation(phi)
    def func(x, y, z):
        return mat.get_rotate([x, y, z])
    return func

class Star(object):

    def __init__(self, pos, rescale, n):
        tex_name, sphere_radius, phi, orbital_radius = _data[n]
        func = _high_func(sphere_radius, phi, rescale)
        self.radius = sphere_radius * rescale
        self.radius2 = self.radius**2
        self.model = Polygon(IMG_DIR+"star", func=func, texture=False)
        self.model.set_texture(tex_name)
        self.X = pos + Vector4D(0.0, 0.0, 0.0, -orbital_radius*rescale)

    def draw(self, Xp, L):
        dX = self.X - Xp
        dX.t = -dX.length()
        dx = L.get_transform_v4(dX)
        r = -dx.t
        if r > 0.5*BOX.far_clip:
            s = 0.05 * BOX.far_clip / r
            X = Xp + dX*s
            self.model.draw(Xp, L, X=X, R=Matrix44.scale(s))
        else:
            self.model.draw(Xp, L, X=self.X)

    def hit_check(self, Xp, world):
        t = Xp.t - Xp.distance_to(self.X)
        self.X.t = t
        X1 = self.X + Vector4D(0.02, 0, 0, 0)
        world.player.bullet_hit_check(X1, self.X, self.radius2)
        world.enemies.bullets.hit_check(X1, self.X, self.radius2)

class Stars(object):

    def __init__(self, world, pos, scale):
        self.world = world
        rescale = 1.0 / c
        self.stars = [Star(pos, rescale, i) for i in xrange(len(_data))]

    def draw(self, Xp, L):
        for star in self.stars:
            star.draw(Xp, L)

    def hit_check(self, Xp):
        for star in self.stars:
            star.hit_check(Xp, self.world)

