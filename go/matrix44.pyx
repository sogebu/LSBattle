# coding: utf8
# cython: profile=False
# go/matrix44.pyx
cimport cython
from libc.math cimport sqrt, sin, cos
DEF pi = 3.141592653589793115997963468544185161590576171875

from vector3 cimport Vector3, vec3_from_floats
from vector4D cimport Vector4D, vec4_from_floats
from matrix44 cimport Matrix44, Lorentz


cdef class Matrix44(object):

    def __init__(self, m=None):
        if m:
            self.m00 = m[ 0]; self.m01 = m[ 1]; self.m02 = m[ 2]; self.m03 = m[ 3]
            self.m10 = m[ 4]; self.m11 = m[ 5]; self.m12 = m[ 6]; self.m13 = m[ 7]
            self.m20 = m[ 8]; self.m21 = m[ 9]; self.m22 = m[10]; self.m23 = m[11]
            self.m30 = m[12]; self.m31 = m[13]; self.m32 = m[14]; self.m33 = m[15]
        else:
            self.m00 = 1.0; self.m01 = 0.0; self.m02 = 0.0; self.m03 = 0.0
            self.m10 = 0.0; self.m11 = 1.0; self.m12 = 0.0; self.m13 = 0.0
            self.m20 = 0.0; self.m21 = 0.0; self.m22 = 1.0; self.m23 = 0.0
            self.m30 = 0.0; self.m31 = 0.0; self.m32 = 0.0; self.m33 = 1.0

    def _get_row_1(self):
        return vec3_from_floats(self.m11, self.m12, self.m13)
    def _set_row_1(self, values):
        self.m11 = values[0] * 1.0
        self.m12 = values[1] * 1.0
        self.m13 = values[2] * 1.0

    def _get_row_2(self):
        return vec3_from_floats(self.m21, self.m22, self.m23)
    def _set_row_2(self, values):
        self.m21 = values[0] * 1.0
        self.m22 = values[1] * 1.0
        self.m23 = values[2] * 1.0

    def _get_row_3(self):
        return vec3_from_floats(self.m31, self.m32, self.m33)
    def _set_row_3(self, values):
        self.m31 = values[0] * 1.0
        self.m31 = values[1] * 1.0
        self.m33 = values[2] * 1.0

    _row1 = property(_get_row_1, _set_row_1, None, "Row 1")
    _row2 = property(_get_row_2, _set_row_2, None, "Row 2")
    _row3 = property(_get_row_3, _set_row_3, None, "Row 3")

    right     = _row1
    up        = _row2
    forward   = _row3

    def copy(self):
        cdef Matrix44 m = Matrix44.__new__(Matrix44)
        m.m00 = self.m00; m.m01 = self.m01; m.m02 = self.m02; m.m03 = self.m03
        m.m10 = self.m10; m.m11 = self.m11; m.m12 = self.m12; m.m13 = self.m13
        m.m20 = self.m20; m.m21 = self.m21; m.m22 = self.m22; m.m23 = self.m23
        m.m30 = self.m30; m.m31 = self.m31; m.m32 = self.m32; m.m33 = self.m33
        return m
    __copy__ = copy

    @classmethod
    def x_rotation(cls, double angle):
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        cdef Matrix44 m = Matrix44.__new__(Matrix44)
        m.m00 = 1.0; m.m01 = 0.0; m.m02 =   0.0; m.m03 =    0.0
        m.m10 = 0.0; m.m11 = 1.0; m.m12 =   0.0; m.m13 =    0.0
        m.m20 = 0.0; m.m21 = 0.0; m.m22 = cos_a; m.m23 = -sin_a
        m.m30 = 0.0; m.m31 = 0.0; m.m32 = sin_a; m.m33 =  cos_a
        return m

    @classmethod
    def y_rotation(cls, double angle):
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        cdef Matrix44 m = Matrix44.__new__(Matrix44)
        m.m00 = 1.0; m.m01 =    0.0; m.m02 = 0.0; m.m03 =   0.0
        m.m10 = 0.0; m.m11 =  cos_a; m.m12 = 0.0; m.m13 = sin_a
        m.m20 = 0.0; m.m21 =    0.0; m.m22 = 1.0; m.m23 =   0.0
        m.m30 = 0.0; m.m31 = -sin_a; m.m32 = 0.0; m.m33 = cos_a
        return m

    @classmethod
    def z_rotation(cls, double angle):
        cdef double cos_a = cos(angle)
        cdef double sin_a = sin(angle)
        cdef Matrix44 m = Matrix44.__new__(Matrix44)
        m.m00 = 1.0; m.m01 =   0.0; m.m02 =    0.0; m.m03 = 0.0
        m.m10 = 0.0; m.m11 = cos_a; m.m12 = -sin_a; m.m13 = 0.0
        m.m20 = 0.0; m.m21 = sin_a; m.m22 =  cos_a; m.m23 = 0.0
        m.m30 = 0.0; m.m31 =   0.0; m.m32 =    0.0; m.m33 = 1.0
        return m

    @classmethod
    def scale(cls, double scale):
        cdef Matrix44 m = Matrix44.__new__(Matrix44)
        m.m00 = 1.0; m.m01 =   0.0; m.m02 =   0.0; m.m03 =   0.0
        m.m10 = 0.0; m.m11 = scale; m.m12 =   0.0; m.m13 =   0.0
        m.m20 = 0.0; m.m21 =   0.0; m.m22 = scale; m.m23 =   0.0
        m.m30 = 0.0; m.m31 =   0.0; m.m32 =   0.0; m.m33 = scale
        return m

    def __mul__(Matrix44 self, Matrix44 rhs):
        """
        self: Matrix44
        rhs: Matrix44
        -> self*rhs

        This differs from the original McGugan's notation
        that returns rhs*self (in Mathematical language).
        """

        cdef Matrix44 ret = Matrix44.__new__(Matrix44)
        ret.m00 = self.m00*rhs.m00 + self.m01*rhs.m10 + self.m02*rhs.m20 + self.m03*rhs.m30
        ret.m01 = self.m00*rhs.m01 + self.m01*rhs.m11 + self.m02*rhs.m21 + self.m03*rhs.m31
        ret.m02 = self.m00*rhs.m02 + self.m01*rhs.m12 + self.m02*rhs.m22 + self.m03*rhs.m32
        ret.m03 = self.m00*rhs.m03 + self.m01*rhs.m13 + self.m02*rhs.m23 + self.m03*rhs.m33

        ret.m10 = self.m10*rhs.m00 + self.m11*rhs.m10 + self.m12*rhs.m20 + self.m13*rhs.m30
        ret.m11 = self.m10*rhs.m01 + self.m11*rhs.m11 + self.m12*rhs.m21 + self.m13*rhs.m31
        ret.m12 = self.m10*rhs.m02 + self.m11*rhs.m12 + self.m12*rhs.m22 + self.m13*rhs.m32
        ret.m13 = self.m10*rhs.m03 + self.m11*rhs.m13 + self.m12*rhs.m23 + self.m13*rhs.m33

        ret.m20 = self.m20*rhs.m00 + self.m21*rhs.m10 + self.m22*rhs.m20 + self.m23*rhs.m30
        ret.m21 = self.m20*rhs.m01 + self.m21*rhs.m11 + self.m22*rhs.m21 + self.m23*rhs.m31
        ret.m22 = self.m20*rhs.m02 + self.m21*rhs.m12 + self.m22*rhs.m22 + self.m23*rhs.m32
        ret.m23 = self.m20*rhs.m03 + self.m21*rhs.m13 + self.m22*rhs.m23 + self.m23*rhs.m33

        ret.m30 = self.m30*rhs.m00 + self.m31*rhs.m10 + self.m32*rhs.m20 + self.m33*rhs.m30
        ret.m31 = self.m30*rhs.m01 + self.m31*rhs.m11 + self.m32*rhs.m21 + self.m33*rhs.m31
        ret.m32 = self.m30*rhs.m02 + self.m31*rhs.m12 + self.m32*rhs.m22 + self.m33*rhs.m32
        ret.m33 = self.m30*rhs.m03 + self.m31*rhs.m13 + self.m32*rhs.m23 + self.m33*rhs.m33
        return ret

    def __imul__(Matrix44 self, Matrix44 rhs):
        """
        self: Matrix44
        rhs: Matrix44
        -> self*rhs

        This routine overwrites self by the result of self*rhs.
        This differs from the original McGugan's notation
        that does it with rhs*self (in Mathematical language).
        """
        cdef double m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33
        m00 = self.m00*rhs.m00 + self.m01*rhs.m10 + self.m02*rhs.m20 + self.m03*rhs.m30
        m01 = self.m00*rhs.m01 + self.m01*rhs.m11 + self.m02*rhs.m21 + self.m03*rhs.m31
        m02 = self.m00*rhs.m02 + self.m01*rhs.m12 + self.m02*rhs.m22 + self.m03*rhs.m32
        m03 = self.m00*rhs.m03 + self.m01*rhs.m13 + self.m02*rhs.m23 + self.m03*rhs.m33

        m10 = self.m10*rhs.m00 + self.m11*rhs.m10 + self.m12*rhs.m20 + self.m13*rhs.m30
        m11 = self.m10*rhs.m01 + self.m11*rhs.m11 + self.m12*rhs.m21 + self.m13*rhs.m31
        m12 = self.m10*rhs.m02 + self.m11*rhs.m12 + self.m12*rhs.m22 + self.m13*rhs.m32
        m13 = self.m10*rhs.m03 + self.m11*rhs.m13 + self.m12*rhs.m23 + self.m13*rhs.m33

        m20 = self.m20*rhs.m00 + self.m21*rhs.m10 + self.m22*rhs.m20 + self.m23*rhs.m30
        m21 = self.m20*rhs.m01 + self.m21*rhs.m11 + self.m22*rhs.m21 + self.m23*rhs.m31
        m22 = self.m20*rhs.m02 + self.m21*rhs.m12 + self.m22*rhs.m22 + self.m23*rhs.m32
        m23 = self.m20*rhs.m03 + self.m21*rhs.m13 + self.m22*rhs.m23 + self.m23*rhs.m33

        m30 = self.m30*rhs.m00 + self.m31*rhs.m10 + self.m32*rhs.m20 + self.m33*rhs.m30
        m31 = self.m30*rhs.m01 + self.m31*rhs.m11 + self.m32*rhs.m21 + self.m33*rhs.m31
        m32 = self.m30*rhs.m02 + self.m31*rhs.m12 + self.m32*rhs.m22 + self.m33*rhs.m32
        m33 = self.m30*rhs.m03 + self.m31*rhs.m13 + self.m32*rhs.m23 + self.m33*rhs.m33

        self.m00 = m00; self.m01 = m01; self.m02 = m02; self.m03 = m03
        self.m10 = m10; self.m11 = m11; self.m12 = m12; self.m13 = m13
        self.m20 = m20; self.m21 = m21; self.m22 = m22; self.m23 = m23
        self.m30 = m30; self.m31 = m31; self.m32 = m32; self.m33 = m33
        return self

    def get_inverse_rot(self):
        """
        Returns the inverse of a Matrix44 that is a 3D rotation
        by transposing its 3D rotation part.
        """
        cdef Matrix44 m = Matrix44.__new__(Matrix44)
        m.m00 = self.m00; m.m01 = self.m01; m.m02 = self.m02; m.m03 = self.m03
        m.m10 = self.m10; m.m11 = self.m11; m.m12 = self.m21; m.m13 = self.m31
        m.m20 = self.m20; m.m21 = self.m12; m.m22 = self.m22; m.m23 = self.m32
        m.m30 = self.m30; m.m31 = self.m13; m.m32 = self.m23; m.m33 = self.m33
        return m

    def rotate(self, Vector3 v):
        """
        self: Matrix44
        v: Vector3

        Let M be the 3D rotation part of self.
        This routine overwrites v by M*v.
        """
        cdef double x, y, z
        x = v._x
        y = v._y
        z = v._z

        v._x = self.m11*x + self.m12*y + self.m13*z
        v._y = self.m21*x + self.m22*y + self.m23*z
        v._z = self.m31*x + self.m32*y + self.m33*z

    def get_rotate(self, v):
        """
        self: Matrix44
        v: list of three objects
        -> list of three objects

        Let M be the 3D rotation part of self.
        This routine returns M*v.
        """
        cdef double x, y, z, xx, yy, zz
        x, y, z = v

        xx = self.m11*x + self.m12*y + self.m13*z
        yy = self.m21*x + self.m22*y + self.m23*z
        zz = self.m31*x + self.m32*y + self.m33*z
        return [xx, yy, zz]

    def get_rotate_v3(self, v):
        """
        self: Matrix44
        v: list of three objects
        -> Vector3

        Let M be the 3D rotation part of self.
        This routine returns M*v.
        """
        cdef double x, y, z, xx, yy, zz
        x, y, z = v

        xx = self.m11*x + self.m12*y + self.m13*z
        yy = self.m21*x + self.m22*y + self.m23*z
        zz = self.m31*x + self.m32*y + self.m33*z
        return vec3_from_floats(xx, yy, zz)

    cpdef int transform(self, Vector4D v):
        """
        self: Matrix44
        v: Vector4D

        This routine overwrites v by self*v.
        """
        cdef double t, x, y, z
        t = v._t
        x = v._x
        y = v._y
        z = v._z

        v._t = self.m00*t + self.m01*x + self.m02*y + self.m03*z
        v._x = self.m10*t + self.m11*x + self.m12*y + self.m13*z
        v._y = self.m20*t + self.m21*x + self.m22*y + self.m23*z
        v._z = self.m30*t + self.m31*x + self.m32*y + self.m33*z
        return 0

    cpdef Vector4D get_transform(self, v):
        cdef double t, x, y, z, tt, xx, yy, zz
        t, x, y, z = v

        tt = self.m00*t + self.m01*x + self.m02*y + self.m03*z
        xx = self.m10*t + self.m11*x + self.m12*y + self.m13*z
        yy = self.m20*t + self.m21*x + self.m22*y + self.m23*z
        zz = self.m30*t + self.m31*x + self.m32*y + self.m33*z
        return vec4_from_floats(tt, xx, yy, zz)

    def get_transform_lis3(self, v):
        cdef double t, x, y, z, xx, yy, zz
        t, x, y, z = v

        xx = self.m10*t + self.m11*x + self.m12*y + self.m13*z
        yy = self.m20*t + self.m21*x + self.m22*y + self.m23*z
        zz = self.m30*t + self.m31*x + self.m32*y + self.m33*z
        return [xx, yy, zz]

    def to_opengl(self):
        """
        self: Matrix44
        -> list of 16 floats

        This routine converts the 3D rotation part of self
        into the openGL format.
        """
        return [self.m11, self.m12, self.m13, 0.0,
                self.m21, self.m22, self.m23, 0.0,
                self.m31, self.m32, self.m33, 0.0,
                0.0,           0.0,      0.0, 1.0]

    def to_glsl(self):
        """
        self: Matrix44
        -> list of 16 floats.

        This routine converts self
        into the GLSL format.
        (Note that the transposition is done properly.)
        """
        return [self.m11, self.m21, self.m31, self.m01,
                self.m12, self.m22, self.m32, self.m02,
                self.m13, self.m23, self.m33, self.m03,
                self.m10, self.m20, self.m30, self.m00]

    def get_gamma(self):
        return self.m00

@cython.cdivision(True)
cpdef Matrix44 Lorentz(Vector4D u):
    cdef Matrix44 m = Matrix44.__new__(Matrix44)
    cdef double x, y, z, x2, y2, z2, r, g, xy, yz, zx
    x = u._x
    y = u._y
    z = u._z
    x2 = x*x
    y2 = y*y
    z2 = z*z
    r = x2 + y2 + z2
    if r > 0.0:
        g = sqrt(1.0 + r)
        r = 1.0 / r
        xy = (g-1.0)*x*y*r
        yz = (g-1.0)*y*z*r
        zx = (g-1.0)*z*x*r
        m.m00 =  g; m.m01 =                 -x; m.m02 =                 -y; m.m03 =                 -z
        m.m10 = -x; m.m11 = (g*x2 + y2 + z2)*r; m.m12 =                 xy; m.m13 =                 zx
        m.m20 = -y; m.m21 =                 xy; m.m22 = (x2 + g*y2 + z2)*r; m.m23 =                 yz
        m.m30 = -z; m.m31 =                 zx; m.m32 =                 yz; m.m33 = (x2 + y2 + g*z2)*r
    else:
        m.m00 = 1.0; m.m01 = 0.0; m.m02 = 0.0; m.m03 = 0.0
        m.m10 = 0.0; m.m11 = 1.0; m.m12 = 0.0; m.m13 = 0.0
        m.m20 = 0.0; m.m21 = 0.0; m.m22 = 1.0; m.m23 = 0.0
        m.m30 = 0.0; m.m31 = 0.0; m.m32 = 0.0; m.m33 = 1.0
    return m
