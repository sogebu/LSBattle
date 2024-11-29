# coding: utf8
# cython: profile=False
# go/quaternion.pyx
cimport cython
from libc.math cimport cos, sin, sqrt, acos
DEF pi = 3.141592653589793115997963468544185161590576171875

from matrix44 cimport Matrix44


cdef void _arg0(Quaternion self, args):
    self._t = 1.0
    self._x = 0.0
    self._y = 0.0
    self._z = 0.0
@cython.cdivision(True)
cdef void _arg1(Quaternion self, args):
    cdef double t, x, y, z, r
    t, x, y, z = args[0]
    r = t*t + x*x + y*y + z*z
    if r > 0.0:
        r = 1.0 / sqrt(r)
        self._t = t * r
        self._x = x * r
        self._y = y * r
        self._z = z * r
    else:
        self._t = 1.0
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0
@cython.cdivision(True)
cdef void _arg2(Quaternion self, args):
    cdef double t, x, y, z, r
    t, (x, y, z) = args
    r = t*t + x*x + y*y + z*z
    if r > 0.0:
        r = 1.0 / sqrt(r)
        self._t = t * r
        self._x = x * r
        self._y = y * r
        self._z = z * r
    else:
        self._t = 1.0
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0
@cython.cdivision(True)
cdef void _arg3(Quaternion self, args):
    cdef double x, y, z, r
    x, y, z = args
    r = x*x + y*y + z*z
    if r > 1.0:
        r = 1.0 / sqrt(r)
        self._t = 0.0
        self._x = x * r
        self._y = y * r
        self._z = z * r
    elif r > 0.0:
        self._t = 1.0 - sqrt(r)
        self._x = x
        self._y = y
        self._z = z
    else:
        self._t = 1.0
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0
@cython.cdivision(True)
cdef void _arg4(Quaternion self, args):
    cdef double t, x, y, z, r
    t, x, y, z = args
    r = t*t + x*x + y*y + z*z
    if r > 0.0:
        r = 1.0 / sqrt(r)
        self._t = t * r
        self._x = x * r
        self._y = y * r
        self._z = z * r
    else:
        self._t = 1.0
        self._x = 0.0
        self._y = 0.0
        self._z = 0.0
cdef void (*_args[5])(Quaternion self, args)
_args[0] = _arg0
_args[1] = _arg1
_args[2] = _arg2
_args[3] = _arg3
_args[4] = _arg4


cdef class Quaternion(object):
    cdef double _t, _x, _y, _z

    def __init__(self, *args):
       _args[len(args)](self, args)

    cpdef Quaternion from_floats(self, double t, double x, double y, double z):
        cdef Quaternion v = Quaternion.__new__(Quaternion)
        v._t = t
        v._x = x
        v._y = y
        v._z = z
        return v

    @classmethod
    def from_ax(cls, double theta, ax):
        cdef double c, s, x, y, z
        c = cos(theta*0.5)
        s = sin(theta*0.5)
        x, y, z = ax
        cdef Quaternion v = Quaternion.__new__(Quaternion)
        v._t = c
        v._x = x * s
        v._y = y * s
        v._z = z * s
        return v

    @cython.cdivision(True)
    @classmethod
    def from_RotMat(cls, Matrix44 R):
        cdef double m, n, e
        cdef int i
        m = R.m00 + R.m11 + R.m22 + 1.0
        n = R.m00 - R.m11 - R.m22 + 1.0
        i = 0
        if m < n:
            m = n
            i = 1
        n = R.m11 - R.m22 - R.m00 + 1.0
        if m < n:
            m = n
            i = 2
        n = R.m22 - R.m00 - R.m11 + 1.0
        if m < n:
            m = n
            i = 3

        e = sqrt(m) * 0.5
        m = 0.25 / e
        cdef Quaternion v = Quaternion.__new__(Quaternion)
        if i == 0:
            v._t = e
            v._x = (R.m21 - R.m12) * m
            v._y = (R.m02 - R.m20) * m
            v._z = (R.m10 - R.m01) * m
        elif i == 1:
            v._t = (R.m21 - R.m12) * m
            v._x =  e
            v._y = (R.m01 + R.m10) * m
            v._z = (R.m02 + R.m20) * m
        elif i == 2:
            v._t = (R.m02 - R.m20) * m
            v._x = (R.m01 + R.m10) * m
            v._y = e
            v._z = (R.m12 + R.m21) * m
        else:
            v._t = (R.m10 - R.m01) * m
            v._x = (R.m02 + R.m20) * m
            v._y = (R.m12 + R.m21) * m
            v._z = e
        return v

    def get_RotMat(self):
        cdef double x2, y2, z2, tx, ty, tz, xy, yz, zx
        x2 = 2.0*self._x*self._x
        y2 = 2.0*self._y*self._y
        z2 = 2.0*self._z*self._z
        tx = 2.0*self._t*self._x
        ty = 2.0*self._t*self._y
        tz = 2.0*self._t*self._z
        xy = 2.0*self._x*self._y
        yz = 2.0*self._y*self._z
        zx = 2.0*self._z*self._x
        return Matrix44([1.0,      0.0,        0.0,       0.0,
                         0.0, 1.0-y2-z2,   xy - tz,   zx + ty,
                         0.0,   xy + tz, 1.0-z2-x2,   yz - tx,
                         0.0,   zx - ty,   yz + tx, 1.0-x2-y2])

    def get_right_lis3_i(self):
        cdef double y2, z2, ty, tz, xy, zx
        y2 = 2.0*self._y*self._y
        z2 = 2.0*self._z*self._z
        ty = 2.0*self._t*self._y
        tz = 2.0*self._t*self._z
        xy = 2.0*self._x*self._y
        zx = 2.0*self._z*self._x
        return [1.0-y2-z2, xy + tz, zx - ty]
    def get_right_lis3(self):
        cdef double y2, z2, ty, tz, xy, zx
        y2 = 2.0*self._y*self._y
        z2 = 2.0*self._z*self._z
        ty = 2.0*self._t*self._y
        tz = 2.0*self._t*self._z
        xy = 2.0*self._x*self._y
        zx = 2.0*self._z*self._x
        return [1.0-y2-z2, xy - tz, zx + ty]

    def get_upward_lis3_i(self):
        cdef double x2, z2, tx, tz, xy, yz
        x2 = 2.0*self._x*self._x
        z2 = 2.0*self._z*self._z
        tx = 2.0*self._t*self._x
        tz = 2.0*self._t*self._z
        xy = 2.0*self._x*self._y
        yz = 2.0*self._y*self._z
        return [xy - tz, 1.0-z2-x2,   yz + tx]
    def get_upward_lis3(self):
        cdef double x2, z2, tx, tz, xy, yz
        x2 = 2.0*self._x*self._x
        z2 = 2.0*self._z*self._z
        tx = 2.0*self._t*self._x
        tz = 2.0*self._t*self._z
        xy = 2.0*self._x*self._y
        yz = 2.0*self._y*self._z
        return [xy + tz, 1.0-z2-x2,   yz - tx]

    def get_forward_lis3_i(self):
        cdef double x2, y2, tx, ty, yz, zx
        x2 = 2.0*self._x*self._x
        y2 = 2.0*self._y*self._y
        tx = 2.0*self._t*self._x
        ty = 2.0*self._t*self._y
        yz = 2.0*self._y*self._z
        zx = 2.0*self._z*self._x
        return [zx + ty, yz - tx, 1.0-x2-y2]
    def get_forward_lis3(self):
        cdef double x2, y2, tx, ty, yz, zx
        x2 = 2.0*self._x*self._x
        y2 = 2.0*self._y*self._y
        tx = 2.0*self._t*self._x
        ty = 2.0*self._t*self._y
        yz = 2.0*self._y*self._z
        zx = 2.0*self._z*self._x
        return [zx - ty, yz + tx, 1.0-x2-y2]

    def copy(self):
        return self.from_floats(self._t, self._x, self._y, self._z)
    __copy__ = copy

    def __repr__(self):
        return "Quaternion(%f, %f, %f, %f)"%(self._t, self._x, self._y, self._z)

    def __str__(self):
        return "(%f; %f, %f, %f)"%(self._t, self._x, self._y, self._z)

    def __iter__(self):
        yield self._t
        yield self._x
        yield self._y
        yield self._z

    def __mul__(Quaternion self, Quaternion rhs):
        cdef double t, x, y, z
        t = self._t*rhs._t - self._x*rhs._x - self._y*rhs._y - self._z*rhs._z
        x = self._t*rhs._x + self._x*rhs._t + self._y*rhs._z - self._z*rhs._y
        y = self._t*rhs._y + self._y*rhs._t + self._z*rhs._x - self._x*rhs._z
        z = self._t*rhs._z + self._z*rhs._t + self._x*rhs._y - self._y*rhs._x
        return self.from_floats(t, x, y, z)

    def __imul__(Quaternion self, Quaternion rhs):
        cdef double t, x, y, z
        t = self._t*rhs._t - self._x*rhs._x - self._y*rhs._y - self._z*rhs._z
        x = self._t*rhs._x + self._x*rhs._t + self._y*rhs._z - self._z*rhs._y
        y = self._t*rhs._y + self._y*rhs._t + self._z*rhs._x - self._x*rhs._z
        z = self._t*rhs._z + self._z*rhs._t + self._x*rhs._y - self._y*rhs._x
        self._t = t
        self._x = x
        self._y = y
        self._z = z
        return self

    @cython.cdivision(True)
    def get_spherep(self, Quaternion othr, double t):
        cdef double a = self._t*self._t + self._x*self._x + self._y*self._y + self._z*self._z
        cdef double b = othr._t*othr._t + othr._x*othr._x + othr._y*othr._y + othr._z*othr._z
        cdef double c = self._t*othr._t + self._x*othr._x + self._y*othr._y + self._z*othr._z
        cdef double l = sqrt(a*b*1.0000005)
        cdef double w = acos(c / l)
        cdef double sinw = sin(w)
        if sinw == 0.0:
            return self.from_floats(self._t, self._x, self._y, self._z)
        cdef double s1 = sin((1.0 - t)*w) / sinw
        cdef double s2 = sin(t*w) / sinw
        return self.from_floats(s1*self._t + s2*othr._t,
                                s1*self._x + s2*othr._x,
                                s1*self._y + s2*othr._y,
                                s1*self._z + s2*othr._z)
