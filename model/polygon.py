# -*- coding: utf8 -*-
# polygon.py
import os

from OpenGL.GL import *

from go import Vector4D, Matrix44, Lorentz
from model.mqo.mqo2gpo import mqo2gpo
from program.utils import load_texture, search_imagefile, compile_program


class Material(object):
    def __init__(self, color, tex_name=None, texture=True, path=""):
        self.color = color
        if tex_name and texture:
            #tex_name = search_imagefile(self.tex_name)
            tex_name = os.path.join(path, tex_name)
            self.tex_name = tex_name
            self.texture_id = load_texture(tex_name)
        else:
            self.tex_name = None
            self.texture_id = None

    def reload_texture(self):
        if self.tex_name is not None:
            self.texture_id = load_texture(self.tex_name)


class MqoGpoPolygon(object):
    def load_gpo(self, name, func=lambda x,y,z:(x,y,z), texture=True):
        igpo = open(name)
        if next(igpo).strip() != "Game Polygon Object":
            raise IOError("%s is not gpo file"%name)
        path, name = os.path.split(name)
        self.path = path
        vertices = []
        texcoords = []
        objects = []
        for line in igpo:
            words = line.split()
            if not words:continue
            if words[0] == "p":
                x, y, z, u, v = list(map(float, words[1:]))
                vertices.extend(func(x, y, z))
                texcoords.extend([u, v])
            elif words[0] == "m":
                color = list(map(float, words[1:-1]))
                tex_name = words[-1][1:-1]
                objects.append([Material(color, tex_name, texture, path), []])
            elif words[0] == "i":
                objects[-1][1] = list(map(int, words[1:]))

        self.vertices = (GLfloat*len(vertices))(*vertices)
        self.texcoords = (GLfloat*len(texcoords))(*texcoords)

        self.objects = []
        for material, indices in objects:
            n = len(indices)
            obj = [material, n, (GLuint*n)(*indices)]
            self.objects.append(obj)

    def set_texture(self, tex_name):
        def _set(self, i, name):
            if os.path.isfile(os.path.join(self.path, name)):
                name = os.path.join(self.path, name)
                self.objects[i][0].texture_id = load_texture(name)
                self.objects[i][0].tex_name = name
            else:
                name = search_imagefile(name)
                self.objects[i][0].texture_id = load_texture(name)
                self.objects[i][0].tex_name = name
        if isinstance(tex_name, list) or isinstance(tex_name, tuple):
            for i, name in enumerate(tex_name):
                _set(self, i, name)
        else:
            _set(self, 0, tex_name)

    def make_gpo(self, name, ext=""):
        if ext.lower() in [".mqo", ".gpo"]:
            if os.path.isfile(name+ext):
                mqo2gpo(name+ext)
                return name + ".gpo"
            elif os.path.isdir(name):
                name = os.path.join(name, os.path.split(name)[1])
                return self.make_gpo(name, ext)
        elif ext == "":
            if os.path.isfile(name+".gpo"):
                if os.path.isfile(name+".mqo"):
                    if os.path.getmtime(name+".mqo") > os.path.getmtime(name+".gpo"):
                        mqo2gpo(name+".mqo")
                return name + ".gpo"
            elif os.path.isfile(name+".mqo"):
                mqo2gpo(name+".mqo")
                return name + ".gpo"
            elif os.path.isdir(name):
                name = os.path.join(name, os.path.split(name)[1])
                return self.make_gpo(name, ext)
            else:
                raise IOError("%s's model file is not exsit"%(os.path.split(name)[1]))
        raise IOError("%s's model file is not exsit"%(os.path.split(name)[1]+ext))

vs_T = """
#version 120
uniform vec4 color;
uniform mat4 Lorentz;
uniform mat4 Lorentz_p2e;
uniform mat4 Rotate;
uniform vec4 dX;
uniform vec4 xp;
varying float ratio;
void main() {
    vec4 xi = Rotate * gl_Vertex;
    xi.w = xp.w - distance(xp.xyz, xi.xyz);
    xi = dX + Lorentz * xi;
    xi.w = -length(xi.xyz);
    vec4 tmp = Lorentz_p2e * xi;
    ratio = xi.w / tmp.w;
    xi.w = 1.0;
    gl_Position = gl_ModelViewProjectionMatrix * xi;
    %s
}
"""
fs_T = """
#version 120
%s
varying float ratio;
void main() {
    %s
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
    gl_FragColor = color / 255.0;
}
"""
_polygon_cache = {}
class Polygon(MqoGpoPolygon):
    def load_program_tex(self):
        self.program_tex = compile_program(
            vs_T%("""
                gl_TexCoord[0] = gl_MultiTexCoord0;
                gl_FrontColor = color;
                """),
            fs_T%("uniform sampler2D texture;",
                  "vec4 color = texture2D(texture, gl_TexCoord[0].xy) * gl_Color;")
        )
        self.t_color_local = glGetUniformLocation(self.program_tex, "color")
        self.t_L_local = glGetUniformLocation(self.program_tex, "Lorentz")
        self.t_Lpe_local = glGetUniformLocation(self.program_tex, "Lorentz_p2e")
        self.t_R_local = glGetUniformLocation(self.program_tex, "Rotate")
        self.t_dX_local = glGetUniformLocation(self.program_tex, "dX")
        self.t_xp_local = glGetUniformLocation(self.program_tex, "xp")
        self.tex_local = glGetUniformLocation(self.program_tex, "texture")

    def load_program_col(self):
        self.program_col = compile_program(
            vs_T%("gl_FrontColor = gl_Color * color;"),
            fs_T%("", "vec4 color = gl_Color;")
        )
        self.c_color_local = glGetUniformLocation(self.program_col, "color")
        self.c_L_local = glGetUniformLocation(self.program_col, "Lorentz")
        self.c_Lpe_local = glGetUniformLocation(self.program_col, "Lorentz_p2e")
        self.c_R_local = glGetUniformLocation(self.program_col, "Rotate")
        self.c_dX_local = glGetUniformLocation(self.program_col, "dX")
        self.c_xp_local = glGetUniformLocation(self.program_col, "xp")

    def __init__(self, name, func=lambda x,y,z:(x,y,z),
                 texture=True, color=(1.0,1.0,1.0,1.0)):
        self.load_program_col()
        self.load_program_tex()
        name, ext = os.path.splitext(name)
        if name in _polygon_cache:
            poly = _polygon_cache[name]
            if func(1.0, 1.0, 1.0) == poly.func(1.0, 1.0, 1.0):
                self.vertices = poly.vertices
                self.texcoords = poly.texcoords
                self.objects = poly.objects
                self.color = color
                self.texture = texture
                self.path = poly.path
                for obj in self.objects:
                    obj[0].reload_texture()
                return
        file_name = self.make_gpo(name, ext)
        self.load_gpo(file_name, func, texture)
        self.color = color
        self.func = func
        self.texture = texture
        _polygon_cache[name] = self

    def draw(self, Xp, L, LL, X=Vector4D(0,0,0,0), U=Vector4D(1,0,0,0), R=Matrix44()):
        """
        Xp: player's X in background frame
        L: background to player frame
        LL: player to background frame
        U: enemy's U in background frame
        X: enemy's X in background frame
        R: enemy's rotation matrix
        """
        # dX: X-Xp in background frame
        dX = X - Xp
        dX.t = -dX.length()
        xp = Lorentz(U).get_transform(-dX)

        # xp: Xp-X in enemy frame
        xp = [xp.x, xp.y, xp.z, xp.t]

        # dX: now, X-Xp in player frame
        dX = L.get_transform_lis3(dX) + [0.0]

        # LL: player to background, then background to enemy
        LL = (Lorentz(U) * LL).to_glsl()

        # L: now, enemy to player
        L = (L * Lorentz(-U)).to_glsl()

        R = R.to_glsl()
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        glTexCoordPointer(2, GL_FLOAT, 0, self.texcoords)
        program = 0
        for material, n, indices in self.objects:
            if material.texture_id is None:
                glColor(*material.color)
                if self.program_col != program:
                    glUseProgram(self.program_col)
                    glUniformMatrix4fv(self.c_L_local, 1, GL_FALSE, L)
                    glUniformMatrix4fv(self.c_Lpe_local, 1, GL_FALSE, LL)
                    glUniformMatrix4fv(self.c_R_local, 1, GL_FALSE, R)
                    glUniform4fv(self.c_dX_local, 1, dX)
                    glUniform4fv(self.c_xp_local, 1, xp)
                    glUniform4fv(self.c_color_local, 1, self.color)
                    program = self.program_col
            else:
                glBindTexture(GL_TEXTURE_2D, material.texture_id)
                if self.program_tex != program:
                    glUseProgram(self.program_tex)
                    glUniformMatrix4fv(self.t_L_local, 1, GL_FALSE, L)
                    glUniformMatrix4fv(self.t_Lpe_local, 1, GL_FALSE, LL)
                    glUniformMatrix4fv(self.t_R_local, 1, GL_FALSE, R)
                    glUniform4fv(self.t_dX_local, 1, dX)
                    glUniform4fv(self.t_xp_local, 1, xp)
                    glUniform4fv(self.t_color_local, 1, self.color)
                    glUniform1i(self.tex_local, 0)
                    program = self.program_tex
            glDrawElements(GL_TRIANGLES, n, GL_UNSIGNED_INT, indices)
        glUseProgram(0)
