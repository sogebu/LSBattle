# -*- coding: utf8 -*-
# pointsplite.py
from OpenGL.GL import *

from program.utils import compile_program, load_texture, DY_TEXTURE_KYU


_vshader = """
#version 120
%s float size;
uniform vec3 Xp;
uniform mat4 lorentz;
void main() {
    vec3 v = gl_Vertex.xyz - Xp;
    vec4 vertex = lorentz * vec4(v, -length(v));
    float r = -vertex.w * 0.2;
    %svertex /= r;
    vertex.w = 1.0;
    gl_Position = gl_ModelViewProjectionMatrix * vertex;
    %s;
    vec4 color = gl_Color;
    %scolor.a = min(color.a, color.a/pow(r,2)*100);
    gl_FrontColor = color;
}
"""
_fshader = """
#version 120
uniform sampler2D texture;
void main() {
    vec4 color = gl_Color * texture2D(texture, gl_PointCoord.xy);
    if(color.a == 0.0) discard;
    gl_FragColor = color;
}
"""

class PointSprite(object):

    def __init__(self, vertices=None, size=None, color=None, size_w=True, texture=DY_TEXTURE_KYU):
        if vertices is not None:
            n = len(vertices)
            self.vertices = (GLfloat*n)(*vertices)
            self.n = n / 3
        if size is None:
            size_type = "attribute"
            size_local_geter = glGetAttribLocation
        else:
            self.size = size
            size_type = "uniform"
            size_local_geter = glGetUniformLocation
        self._draw = getattr(self, "_draw_%i_%i"%(1 if vertices is None else 0,
                                                  1 if size is None else 0)
                            )

        self.color = color

        if size_w:
            psize = "gl_PointSize = size / gl_Position.w"
            color_decay = ""
            normalize_to_look = "//"
        else:
            psize = "gl_PointSize = size"
            color_decay = "//"
            normalize_to_look = ""
        self.program_id = compile_program(
            _vshader%(size_type,
                normalize_to_look,
                psize,
                color_decay),
            _fshader)
        self.size_local = size_local_geter(self.program_id, "size")
        self.vec_local  = glGetUniformLocation(self.program_id, "Xp")
        self.mat_local  = glGetUniformLocation(self.program_id, "lorentz")
        self.tex_local  = glGetUniformLocation(self.program_id, "texture")

        self.texture_id = load_texture(texture)

    def draw(self, Xp, L, vertices=None, size=None, color=None):
        glUseProgram(self.program_id)
        if color is None:
            glColor(*self.color)
        else:
            glColor(*color)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glUniform1i(self.tex_local, 0)
        glUniform3fv(self.vec_local, 1, Xp.get_lis3())
        glUniformMatrix4fv(self.mat_local, 1, GL_FALSE, L.to_glsl())
        self._draw(vertices, size)
        glUseProgram(0)

    def _draw_0_0(self, vertices, size):
        if size is None:
            glUniform1f(self.size_local, self.size)
        else:
            glUniform1f(self.size_local, size)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glDrawArrays(GL_POINTS, 0, self.n)
    def _draw_0_1(self, vertices, sizes):
        glEnableVertexAttribArray(self.size_local)
        glVertexAttribPointer(self.size_local, 1, GL_FLOAT, GL_FALSE, 0, (GLfloat*self.n)(*sizes))
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glDrawArrays(GL_POINTS, 0, self.n)
        glDisableVertexAttribArray(self.size_local)
    def _draw_1_0(self, vertices, size):
        if size is None:
            glUniform1f(self.size_local, self.size)
        else:
            glUniform1f(self.size_local, size)
        n = len(vertices)
        glVertexPointer(3, GL_FLOAT, 0, (GLfloat*n)(*vertices))
        glDrawArrays(GL_POINTS, 0, n//3)
    def _draw_1_1(self, vertices, sizes):
        n = len(sizes)
        glEnableVertexAttribArray(self.size_local)
        glVertexAttribPointer(self.size_local, 1, GL_FLOAT, GL_FALSE, 0, (GLfloat*n)(*sizes))
        glVertexPointer(3, GL_FLOAT, 0, (GLfloat*(n*3))(*vertices))
        glDrawArrays(GL_POINTS, 0, n)
        glDisableVertexAttribArray(self.size_local)

_vshader_doppler = """
#version 120
%s float size;
uniform vec3 Xp;
uniform mat4 lorentz;
attribute vec4 UU;// bullet speed in backgrund
void main() {
    vec3 v = gl_Vertex.xyz - Xp;
    vec4 xi = vec4(v, -length(v)); // in background
    vec4 vertex = lorentz * xi; // in player frame

    vec4 U = UU / sqrt(-(dot(UU.xyz, UU.xyz) - UU.w*UU.w));
    float x2 = U.x * U.x;
    float y2 = U.y * U.y;
    float z2 = U.z * U.z;
    float rr = x2 + y2 + z2;
    float g = sqrt(1.0 + rr);
    float xx, yy, zz, xy, yz, zx;
    if (rr > 0.0) {
        xx = (g*x2 + y2 + z2) / rr;
        yy = (x2 + g*y2 + z2) / rr;
        zz = (x2 + y2 + g*z2) / rr;
        xy = (g - 1.0) * U.x * U.y / rr;
        yz = (g - 1.0) * U.y * U.z / rr;
        zx = (g - 1.0) * U.z * U.x / rr;
    } else {
        xx = 0.0; yy = 0.0; zz = 0.0;
        xy = 0.0; yz = 0.0; zx = 0.0;
    }
    mat4 lorentz_e = mat4(
        xx, xy, zx, -U.x,
        xy, yy, yz, -U.y,
        zx, yz, zz, -U.z,
        -U.x, -U.y, -U.z, g);
    vec4 vertex_e = lorentz_e * xi; // in enemy frame
    float ratio = vertex.w / vertex_e.w;
    float r = -vertex.w * 0.2;
    %svertex /= r;
    vertex.w = 1.0;
    gl_Position = gl_ModelViewProjectionMatrix * vertex;
    %s;
    vec4 color = gl_Color;
    %scolor.a = min(color.a, color.a/pow(r,2)*100);
    color *= 255.0;
    float l = max(max(color.r, color.g), color.b);
    float Tr, Tg, Tb;
    if (l > 1) {
        color *= 255.0 / l;
        Tb = 1000.0 + 904.495*exp(0.00721929 * color.b);
        Tr = 6000.0 + 8.01879e20 * pow(max(color.r, 1.0), -7.507239275877164);
        if (color.b > 254.0) {
            Tg = 6502.86;
        } else {
            if (color.b / max(color.r, 1.0) > 0.98084) {
                Tg = 505.192 * exp(0.0100532 * color.g);
            } else {
                Tg = 6000.0 + 3.55446e34 * pow(max(color.g, 1), -13.24242861627803);
            }
        }
        Tr *= ratio;
        Tg *= ratio;
        Tb *= ratio;
        if (1905.0 > Tb) {
            color.b = 0.0;
        } else if (6700.0 < Tb) {
            color.b = 255.0;
        } else {
            color.b = -305.045 + 138.518 * log(0.01 * Tb - 10.0);
        }
        if (6689.0 > Tr) {
            color.r = 255.0;
        } else {
            color.r = 608.873 * pow(Tr - 6000.0, -0.133205);
        }
        if (506.0 > Tg) {
            color.g = 0.0;
        } else if (6502.86 > Tg) {
            color.g = -619.2 + 99.4708 * log(Tg);
        } else {
            color.g = 406.534 * pow(Tg - 6000.0, -0.0755148);
        }
        color *= l / 255.0;
    }
    gl_FrontColor = color / 255.0;
}
"""
class PointSpriteDoppler(object):

    def __init__(self, vertices=None, size=None, color=None, size_w=True, texture=DY_TEXTURE_KYU):
        if vertices is not None:
            n = len(vertices)
            self.vertices = (GLfloat*n)(*vertices)
            self.n = n / 3
        if size is None:
            size_type = "attribute"
            size_local_geter = glGetAttribLocation
        else:
            self.size = size
            size_type = "uniform"
            size_local_geter = glGetUniformLocation
        self._draw = getattr(self, "_draw_%i_%i"%(1 if vertices is None else 0,
                                                  1 if size is None else 0)
                            )

        self.color = color

        if size_w:
            psize = "gl_PointSize = size / gl_Position.w"
            color_decay = ""
            normalize_to_look = "//"
        else:
            psize = "gl_PointSize = size"
            color_decay = "//"
            normalize_to_look = ""
        self.program_id = compile_program(
            _vshader_doppler%(size_type,
                normalize_to_look,
                psize,
                color_decay),
            _fshader)
        self.size_local = size_local_geter(self.program_id, "size")
        self.vec_local  = glGetUniformLocation(self.program_id, "Xp")
        self.U_local  = glGetAttribLocation(self.program_id, "UU")
        self.mat_local  = glGetUniformLocation(self.program_id, "lorentz")
        self.tex_local  = glGetUniformLocation(self.program_id, "texture")

        self.texture_id = load_texture(texture)

    def draw(self, Xp, L, vertices=None, U=None, size=None, color=None):
        glUseProgram(self.program_id)
        if color is None:
            glColor(*self.color)
        else:
            glColor(*color)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glUniform1i(self.tex_local, 0)
        glUniform3fv(self.vec_local, 1, Xp.get_lis3())
        glUniformMatrix4fv(self.mat_local, 1, GL_FALSE, L.to_glsl())
        glEnableVertexAttribArray(self.U_local)
        if U:
            glVertexAttribPointer(self.U_local, 4, GL_FLOAT, GL_FALSE, 0, (GLfloat*len(U))(*U))
        else:
            glVertexAttribPointer(self.U_local, 4, GL_FLOAT, GL_FALSE, 0,
                (GLfloat*(self.n*4))(*([0.0,0.0,0.0,1.0]*self.n)))
        self._draw(vertices, size)
        glUseProgram(0)

    def _draw_0_0(self, vertices, size):
        if size is None:
            glUniform1f(self.size_local, self.size)
        else:
            glUniform1f(self.size_local, size)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glDrawArrays(GL_POINTS, 0, self.n)

    def _draw_0_1(self, vertices, sizes):
        glEnableVertexAttribArray(self.size_local)
        glVertexAttribPointer(self.size_local, 1, GL_FLOAT, GL_FALSE, 0, (GLfloat*self.n)(*sizes))
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glDrawArrays(GL_POINTS, 0, self.n)
        glDisableVertexAttribArray(self.size_local)

    def _draw_1_0(self, vertices, size):
        if size is None:
            glUniform1f(self.size_local, self.size)
        else:
            glUniform1f(self.size_local, size)
        n = len(vertices)
        glVertexPointer(3, GL_FLOAT, 0, (GLfloat*n)(*vertices))
        glDrawArrays(GL_POINTS, 0, n//3)

    def _draw_1_1(self, vertices, sizes):
        n = len(sizes)
        glEnableVertexAttribArray(self.size_local)
        glVertexAttribPointer(self.size_local, 1, GL_FLOAT, GL_FALSE, 0, (GLfloat*n)(*sizes))
        glVertexPointer(3, GL_FLOAT, 0, (GLfloat*(n*3))(*vertices))
        glDrawArrays(GL_POINTS, 0, n)
        glDisableVertexAttribArray(self.size_local)
