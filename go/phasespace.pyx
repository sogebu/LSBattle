# coding: utf8
# cython: profile=False
# go/phasespace.pyx
cimport cython
from libc.math cimport sqrt

from go.vector4D cimport Vector4D, vec4_from_floats
from go.matrix44 cimport Matrix44, Lorentz


cdef class PhaseSpace(object):

    cdef public Vector4D X, U

    def __init__(self, X, U):
        self.X = Vector4D(X)
        self.U = Vector4D(U)

    def copy(self):
        return PhaseSpace(self.X, self.U)

    def get_resist(self, double b):
        return vec4_from_floats(0.0, -self.U._x*b, -self.U._y*b, -self.U._z*b)

    @cython.cdivision(True)
    def transform(self, Vector4D acceleration, double ds):
        self.X._t = self.X._t + self.U._t * ds
        self.X._x = self.X._x + self.U._x * ds
        self.X._y = self.X._y + self.U._y * ds
        self.X._z = self.X._z + self.U._z * ds
        acceleration._t = 0.0
        cdef Matrix44 L = Lorentz(-self.U)
        cdef Vector4D accel = L.get_transform(acceleration)
        cdef double r = accel.length()
        if r > 10.0:
            self.U += accel * (ds*10.0/r)
        else:
            self.U += accel * ds
        self.U._t = sqrt(1.0 + self.U._x*self.U._x + self.U._y*self.U._y + self.U._z*self.U._z)

