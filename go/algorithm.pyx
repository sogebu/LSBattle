# coding: utf8
# cython: profile=False
# go/algorithm.pyx
cimport cython
from libc.math cimport sqrt

from go.vector4D cimport Vector4D
from go.matrix44 cimport Matrix44, Lorentz


@cython.cdivision(True)
def calc_shoot_direction(Vector4D Xp, Vector4D Up, Vector4D X, Vector4D U, double v):
    cdef Matrix44 L = Lorentz(Up)
    cdef Vector4D x = L.get_transform(X-Xp)
    cdef Vector4D u = L.get_transform(U)
    cdef double v2 = v*v
    cdef double a = -v2*u._t*u._t + u._x*u._x + u._y*u._y + u._z*u._z
    cdef double b = -v2*x._t*u._t + x._x*u._x + x._y*u._y + x._z*u._z
    cdef double c = -v2*x._t*x._t + x._x*x._x + x._y*x._y + x._z*x._z
    cdef double D = b*b - a*c
    if D < 0.0:
        return None
    cdef double tau = (b + sqrt(D)) / (-a)
    s = 1.0 / (v * (x._t + tau*u._t))
    dx = (x._x + tau*u._x) * s
    dy = (x._y + tau*u._y) * s
    dz = (x._z + tau*u._z) * s
    return [dx, dy, dz]

@cython.cdivision(True)
def calc_repulsion(Vector4D Xp, Vector4D X1, Vector4D U1, double collision_radius, double repulsion, Vector4D acceleration):
    cdef Vector4D X = Xp - X1
    cdef double R = -U1.inner_product(X)
    if R < collision_radius:
        X.normalize(repulsion * (collision_radius - R))
        X._t = U1.dot(X) / U1._t
        Lorentz(-U1).transform(X)
        acceleration._x += X._x
        acceleration._y += X._y
        acceleration._z += X._z

@cython.cdivision(True)
def hit_check(Vector4D Xs, Vector4D N, double S, Vector4D X1, Vector4D X0, double collision_radius2):
    cdef Vector4D X, dX, Y, dY
    cdef double Nt, Xt, dXt, dot, dY2, tc, s, R2
    X = X0 - Xs
    Nt = 1.0 / N._t
    Xt  =  X._t * Nt
    if Xt > S:
        return
    dX = X1 - X0
    dXt = dX._t * Nt
    Y = X.get_linear_add(N, -Xt)
    dY = dX.get_linear_add(N, -dXt)
    dot = Y.dot(dY)
    if dot < 0.0:
        dY2 = dY.squared_length()
        tc = -dot / dY2
        if tc < 1.0:
            s = Xt + dXt * tc
            R2 = tc*tc*dY2 + 2.0*tc*dot
        else:
            s = Xt + dXt
            R2 = dY2 + 2.0*dot
    else:
        s = Xt
        R2 = 0.0
    if 0.0 < s < S and R2 + Y.squared_length() < collision_radius2:
        return s
