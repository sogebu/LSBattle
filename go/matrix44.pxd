# coding: utf8
# go/matrix44.pxd
from go.vector4D cimport Vector4D


cdef class Matrix44(object):
    cdef double m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33
    cpdef int transform(self, Vector4D v)
    cpdef Vector4D get_transform(self, v)

cpdef Matrix44 Lorentz(Vector4D u)
