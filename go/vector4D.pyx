# coding: utf8
# cython: profile=False
# go/vector4D.pyx
cimport cython
from libc.math cimport sqrt

from vector3 cimport vec3_from_floats
from vector4D cimport Vector4D, vec4_from_floats


cdef void _arg0(Vector4D self, args):
    self._t = 0.0
    self._x = 0.0
    self._y = 0.0
    self._z = 0.0
cdef void _arg1(Vector4D self, args):
    cdef double t, x, y, z
    t, x, y, z = args[0]
    self._t = t
    self._x = x
    self._y = y
    self._z = z
cdef void _arg2(Vector4D self, args):
    cdef double t, x, y, z
    t, (x, y, z) = args
    self._t = t
    self._x = x
    self._y = y
    self._z = z
cdef void _arg3(Vector4D self, args):
    cdef double x, y, z
    x, y, z = args
    self._t = 0.0
    self._x = x
    self._y = y
    self._z = z
cdef void _arg4(Vector4D self, args):
    cdef double t, x, y, z
    t, x, y, z = args
    self._t = t
    self._x = x
    self._y = y
    self._z = z
cdef void (*_args[5])(Vector4D self, args)
_args[0] = _arg0
_args[1] = _arg1
_args[2] = _arg2
_args[3] = _arg3
_args[4] = _arg4

cdef class Vector4D(object):

    def __init__(self, *args):
        _args[len(args)](self, args)

    @classmethod
    def from_tv(cls, double t, v):
        cdef Vector4D u = Vector4D.__new__(Vector4D)
        cdef double x, y, z
        x, y, z = v
        u._t = t
        u._x = x
        u._y = y
        u._z = z
        return u

    cpdef Vector4D copy(self):
        return vec4_from_floats(self._t, self._x, self._y, self._z)
    __copy__ = copy

    def _get_t(self):
        return self._t
    def _set_t(self, double t):
        self._t = t
    t = property(_get_t, _set_t, None, "t component.")

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

    def _get_3d(self):
        return vec3_from_floats(self._x, self._y, self._z)
    def _set_3d(self, v):
        cdef double x, y, z
        x, y, z = v
        self._x = x
        self._y = y
        self._z = z
    d = property(_get_3d, _set_3d, None, "space part")

    def __iter__(self):
        yield self._t
        yield self._x
        yield self._y
        yield self._z

    def __add__(Vector4D lhs, Vector4D rhs):
        return vec4_from_floats(lhs._t+rhs._t, lhs._x+rhs._x, lhs._y+rhs._y, lhs._z+rhs._z)
    def __iadd__(Vector4D self, Vector4D rhs):
        self._t += rhs._t
        self._x += rhs._x
        self._y += rhs._y
        self._z += rhs._z
        return self

    def __sub__(Vector4D lhs, Vector4D rhs):
        return vec4_from_floats(lhs._t-rhs._t, lhs._x-rhs._x, lhs._y-rhs._y, lhs._z-rhs._z)
    def __isub__(Vector4D self, Vector4D rhs):
        self._t -= rhs._t
        self._x -= rhs._x
        self._y -= rhs._y
        self._z -= rhs._z
        return self

    def __mul__(Vector4D self, double rhs):
        return vec4_from_floats(self._t*rhs, self._x*rhs, self._y*rhs, self._z*rhs)
    def __imul__(Vector4D self, double rhs):
        self._t *= rhs
        self._x *= rhs
        self._y *= rhs
        self._z *= rhs
        return self

    def __truediv__(Vector4D self, double rhs):
        rhs = 1.0 / rhs
        return vec4_from_floats(self._t*rhs, self._x*rhs, self._y*rhs, self._z*rhs)
    def __itruediv__(Vector4D self, double rhs):
        rhs = 1.0 / rhs
        self._t *= rhs
        self._x *= rhs
        self._y *= rhs
        self._z *= rhs
        return self

    def __neg__(Vector4D self):
        return vec4_from_floats(-self._t, -self._x, -self._y, -self._z)

    def __pos__(Vector4D self):
        return vec4_from_floats(self._t, self._x, self._y, self._z)

    def __str__(Vector4D self):
        return "(%f, %f, %f, %f)"%(self._t, self._x, self._y, self._z)

    def __repr__(Vector4D self):
        return "Vector4D(%f, %f, %f, %f)"%(self._t, self._x, self._y, self._z)

    cpdef double length(self):
        return sqrt(self._x*self._x + self._y*self._y + self._z*self._z)

    cpdef double squared_length(self):
        return self._x*self._x + self._y*self._y + self._z*self._z

    def distance_to(self, Vector4D othr):
        """
        othr: Vector4D
        -> a number, distance in 3D between spatial components of self and othr.
        """
        cdef double x, y, z
        x = self._x - othr._x
        y = self._y - othr._y
        z = self._z - othr._z
        return sqrt(x*x + y*y + z*z)

    def distance_to_squared(self, Vector4D othr):
        """
        othr: Vector4D
        -> a number, squared distance in 3D between spatial components of self and othr.
        """
        cdef double x, y, z
        x = self._x - othr._x
        y = self._y - othr._y
        z = self._z - othr._z
        return x*x + y*y + z*z

    cpdef double dot(self, Vector4D othr):
        return self._x*othr._x + self._y*othr._y + self._z*othr._z

    def get_gamma(self):
        return sqrt(1.0 + self._x*self._x + self._y*self._y + self._z*self._z)

    cpdef double inner_product(self, Vector4D othr):
        return self._x*othr._x + self._y*othr._y + self._z*othr._z - self._t*othr._t

    cpdef double squared_norm(self):
        return self._x*self._x + self._y*self._y + self._z*self._z - self._t*self._t

    cpdef double squared_norm_to(self, Vector4D othr):
        cdef double t, x, y, z
        t = self._t - othr._t
        x = self._x - othr._x
        y = self._y - othr._y
        z = self._z - othr._z
        return x*x + y*y + z*z - t*t

    @cython.cdivision(True)
    def get_hat(self, double length=1.0):
        """
        self: Vector4D
        length: the length of the returning Vector3.
        -> Vector3

        Normalizes the spatial component of self to "length".
        if length of self vector is 0, return Vector3(length, 0, 0)
        """
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r > 0.0:
            r = length / sqrt(r)
            return vec3_from_floats(self._x*r, self._y*r, self._z*r)
        else:
            return vec3_from_floats(length, 0.0, 0.0)

    @cython.cdivision(True)
    def hat(self, double length=1.0):
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r > 0.0:
            r = length / sqrt(r)
            self._x *= r
            self._y *= r
            self._z *= r
        else:
            self._x = length

    @cython.cdivision(True)
    def get_normalize(self, double length=1.0):
        """
        self: Vector4D
        length: the length of the returning spatial component of Vector4D.
        -> Vector4D

        Normalizes the spatial component of self to "length".
        """
        cdef double  r = self._x*self._x + self._y*self._y + self._z*self._z
        if r > 0.0:
            r = length / sqrt(r)
            return vec4_from_floats(self._t, self._x*r, self._y*r, self._z*r)
        else:
            return vec4_from_floats(self._t, 0.0, 0.0, 0.0)

    @cython.cdivision(True)
    cpdef int normalize(self, double length=1.0):
        cdef double r = self._x*self._x + self._y*self._y + self._z*self._z
        if r > 0.0:
            r = length / sqrt(r)
            self._x *= r
            self._y *= r
            self._z *= r
        return 0

    cpdef Vector4D get_linear_add(self, Vector4D N, double s):
        """
        N: Vector4D
        s: float
        -> self + s*N
        """
        cdef double tt, xx, yy, zz
        tt = self._t + N._t * s
        xx = self._x + N._x * s
        yy = self._y + N._y * s
        zz = self._z + N._z * s
        return vec4_from_floats(tt, xx, yy, zz)

    def get_linear_add_lis3(self, Vector4D N, double s):
        """
        N: Vector4D
        s: float
        -> self + s*N
        """
        cdef double x, y, z
        x = self._x + N._x * s
        y = self._y + N._y * s
        z = self._z + N._z * s
        return [x, y, z]

    cpdef Vector4D get_div_point(self, Vector4D othr, double s):
        """
        othr: Vector4D
        s: float in [0,1]
        -> (1-s)*self + s*othr
        """
        cdef double t, tt, xx, yy, zz
        t = 1.0 - s
        tt = self._t * t + othr._t * s
        xx = self._x * t + othr._x * s
        yy = self._y * t + othr._y * s
        zz = self._z * t + othr._z * s
        return vec4_from_floats(tt, xx, yy, zz)

    def get_lis(self):
        return [self._t, self._x, self._y, self._z]
    def get_lis_glsl(self):
        return [self._x, self._y, self._z, self._t]
    def get_lis3(self):
        return [self._x, self._y, self._z]

cdef Vector4D vec4_from_floats(double t, double x, double y, double z):
    cdef Vector4D v = Vector4D.__new__(Vector4D)
    v._t = t
    v._x = x
    v._y = y
    v._z = z
    return v
