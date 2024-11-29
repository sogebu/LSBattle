# coding: utf8
# cython: profile=False
# go/vector3.pyx
cimport cython
from libc.math cimport sqrt

from vector3 cimport Vector3, vec3_from_floats


cdef void _arg0(Vector3 self, args):
    self._x = 0.0
    self._y = 0.0
    self._z = 0.0
cdef void _arg1(Vector3 self, args):
    cdef double x, y, z
    x, y, z = args[0]
    self._x = x
    self._y = y
    self._z = z
cdef void _arg3(Vector3 self, args):
    cdef double x, y, z
    x, y, z = args
    self._x = x
    self._y = y
    self._z = z
cdef void (*_args[4])(Vector3 self, args)
_args[0] = _arg0
_args[1] = _arg1
_args[2] = NULL
_args[3] = _arg3


cdef class Vector3(object):
    def __init__(self, *args):
        _args[len(args)](self, args)

    cpdef copy(self):
        cdef Vector3 v = Vector3.__new__(Vector3)
        v._x = self._x
        v._y = self._y
        v._z = self._z
        return v
    __copy__ = copy

    def _get_x(self):
        return self._x
    def _set_x(self, double x):
        self._x = x
    x = property(_get_x, _set_x, None, "x component.")

    def _get_y(self):
        return self._y
    def _set_y(self, double y):
        self._y = y
    y = property(_get_y, _set_y, None, "y component.")

    def _get_z(self):
        return self._z
    def _set_z(self, double z):
        self._z = z
    z = property(_get_z, _set_z, None, "z component.")

    def __str__(self):
        return "(%f, %f, %f)"%(self._x, self._y, self._z)

    def __repr__(self):
        return "Vector3(%f, %f, %f)"%(self._x, self._y, self._z)

    def __iter__(self):
        yield self._x
        yield self._y
        yield self._z

    def __add__(Vector3 self, Vector3 rhs):
        return vec3_from_floats(self._x+rhs._x, self._y+rhs._y, self._z+rhs._z)
    def __iadd__(Vector3 self, Vector3 rhs):
        self._x += rhs._x
        self._y += rhs._y
        self._z += rhs._z
        return self

    def __sub__(Vector3 self, Vector3 rhs):
        return vec3_from_floats(self._x-rhs._x, self._y-rhs._y, self._z-rhs._z)
    def __isub__(Vector3 self, Vector3 rhs):
        self._x -= rhs._x
        self._y -= rhs._y
        self._z -= rhs._z
        return self

    def __mul__(Vector3 self, double rhs):
        return vec3_from_floats(self._x*rhs, self._y*rhs, self._z*rhs)
    def __imul__(Vector3 self, double rhs):
        self._x *= rhs
        self._y *= rhs
        self._z *= rhs
        return self

    def __truediv__(Vector3 self, double rhs):
        rhs = 1.0 / rhs
        return vec3_from_floats(self._x*rhs, self._y*rhs, self._z*rhs)
    def __itruediv__(Vector3 self, double rhs):
        rhs = 1.0 / rhs
        self._x *= rhs
        self._y *= rhs
        self._z *= rhs
        return self

    def __neg__(self):
        return vec3_from_floats(-self._x, -self._y, -self._z)

    def __pos__(self):
        return self.copy()

    def get_hat(self, double length=1.0):
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r:
            r = length / sqrt(r)
            return vec3_from_floats(self._x*r, self._y*r, self._z*r)
        else:
            return vec3_from_floats(length, 0.0, 0.0)

    @cython.cdivision(True)
    def hat(self, double length=1.0):
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r:
            r = length / sqrt(r)
            self._x *= r
            self._y *= r
            self._z *= r
        else:
            self._x = length

    @cython.cdivision(True)
    def get_normalize(self, double length=1.0):
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r:
            r = length / sqrt(r)
            return vec3_from_floats(self._x*r, self._y*r, self._z*r)
        else:
            return vec3_from_floats(0.0, 0.0, 0.0)

    @cython.cdivision(True)
    def normalize(self, double length=1.0):
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r:
            r = length / sqrt(r)
            self._x *= r
            self._y *= r
            self._z *= r

    def length(self):
        return sqrt(self._x*self._x + self._y*self._y + self._z*self._z)

    def squared_length(self):
        return self._x*self._x + self._y*self._y + self._z*self._z

    def distance_to(self, Vector3 othr):
        cdef double x, y, z
        x = self._x - othr._x
        y = self._y - othr._y
        z = self._z - othr._z
        return sqrt(x*x + y*y + z*z)

    def distance_to_squared(self, Vector3 othr):
        cdef double x, y, z
        x = self._x - othr._x
        y = self._y - othr._y
        z = self._z - othr._z
        return x*x + y*y + z*z

    def dot(self, othr):
        cdef double x, y, z
        x, y, z = othr
        return self._x*x + self._y*y + self._z*z

    def cross(self, othr):
        cdef double x, y, z
        x, y, z = othr
        return vec3_from_floats( self._y*z - y*self._z,
                                 self._z*x - z*self._x,
                                 self._x*y - x*self._y )

    def get_lis(self):
        return [self._x, self._y, self._z]

cdef Vector3 vec3_from_floats(double x, double y, double z):
    cdef Vector3 v = Vector3.__new__(Vector3)
    v._x = x
    v._y = y
    v._z = z
    return v
