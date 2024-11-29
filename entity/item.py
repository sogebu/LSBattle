# coding: utf8
# entity/item.py
from go import Vector4D, Matrix44
from model.polygon import Polygon
from program.const import IMG_DIR
from program import script


class Item(object):
    def __init__(self, item, X, scale=1.0):
        self.item = item
        self.X = X
        name = script.player.guns[item].model.name
        size = script.player.guns[item].model.size * scale
        color = script.player.guns[item].model.color
        def func(x, y, z):
            return x*size, y*size, z*size
        self.model = Polygon(IMG_DIR+name, func=func, color=color)
        self.time = 0.0
        self.rotation_speed = script.player.guns[item].model.rotation_speed

    def action(self, ds):
        self.time += ds

    def check_collision(self, Xp, r2):
        return Xp.distance_to_squared(self.X) < r2

    def draw(self, Xp, L, LL):
        t = Xp.distance_to_squared(self.X)
        X = Vector4D.from_tv(-t, self.X.d)
        self.model.draw(Xp, L, LL, X, R=Matrix44.y_rotation(self.time*self.rotation_speed))
