# coding: utf8
# cython: profile=False
# go/worldline.pyx
cimport cython
from libc.math cimport sqrt

from go.vector4D cimport Vector4D


cdef class Cache(object):
    cdef public int ix
    cdef public double s
    def __init__(self):
        self.ix = 0
        self.s = 0.0

cdef class WorldLine(object):
    cdef int n
    cdef list line, state
    cdef dict ix_map
    cdef int last

    def __init__(self, P, Q=None):
        self.line  = [P.X.copy()]
        self.state = [Q]
        self.ix_map = {}
        self.n = 1
        self.last = -1

    def set_id(self, ix):
        self.ix_map[ix] = Cache()

    def del_id(self, ix):
        if ix in self.ix_map:
            del self.ix_map[ix]

    def add(self, P, Q=None):
        self.line.append(P.X.copy())
        self.state.append(Q)
        self.n += 1

    def cut(self):
        imin = 0
        for ix in self.ix_map:
            i = self.ix_map[ix].ix
            if i < imin:
                imin = i
        if imin > 0:
            self.line = self.line[imin:]
            self.state = self.state[imin:]
            self.n -= imin

    cdef int search_position_on_PLC(self, Vector4D Xp, long long ix):
        cdef double Xpt = Xp._t
        cdef int start = self.ix_map[ix].ix
        cdef int i
        cdef Vector4D X

        for i in xrange(start, self.n):
            X = self.line[i]
            if X._t > Xpt or Xp.squared_norm_to(X) > 0.0:
                self.ix_map[ix].ix = 0 if i < 1 else i - 1
                return i
        return -1

    @cython.cdivision(True)
    def get_X_FP(self, Xp_py, double w=0.5):
        cdef long long ix = id(Xp_py)
        cdef Vector4D Xp = Xp_py
        cdef int i = self.search_position_on_PLC(Xp, ix)
        if i == -1:
            return None
        cdef Vector4D X0 = self.line[i-1]
        cdef Vector4D X1 = self.line[i]
        cdef Vector4D dX = X0 - X1
        cdef Vector4D dY = X0 - Xp
        cdef double a = dX.squared_norm()
        cdef double b = dX.inner_product(dY)
        cdef double s, c
        if w == 0.5:
            s = b / a
        else:
            c = dY.squared_norm()
            s = (b + (1.0 - 2.0*w)*sqrt(b*b - a*c)) / a
        return X0.get_div_point(X1, s)

    @cython.cdivision(True)
    def get_XU_on_PLC(self, Xp_py):
        cdef long long ix = id(Xp_py)
        cdef Vector4D Xp = Xp_py
        cdef int i = self.search_position_on_PLC(Xp, ix)
        if i == -1:
            return None, None
        cdef Vector4D X0 = self.line[i-1]
        cdef Vector4D X1 = self.line[i]
        cdef Vector4D dX = X1 - X0
        cdef Vector4D dY = Xp - X0
        cdef double a = dX.squared_norm()
        cdef double b = dX.inner_product(dY)
        cdef double c = dY.squared_norm()
        cdef double s = (b + sqrt(b*b - a*c))/a
        self.ix_map[ix].s = s
        dX /= sqrt(-a)
        return X0.get_div_point(X1, s), dX

    def get_State_on_PLC(self, Xp_py):
        cdef long long ix = id(Xp_py)
        cdef int i = self.ix_map[ix].ix
        q0 = self.state[i]
        q1 = self.state[i+1]
        return q0, q1, self.ix_map[ix].s

    def get_last(self):
        return self.line[-1]

    def __len__(self):
        return self.n
