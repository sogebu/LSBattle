#coding: utf8
import operator
import re


class Face(object):
    __slots__ = ("n", "indices", "material", "uv", "h")

    def __init__(self, n=0, indices=None, material=None, uv=None, color=None):
        self.n = int(n)
        if self.n not in [3, 4]:
            self.n = 0
            return
        self.indices = [int(i) for i in indices.split()]
        if len(self.indices) != self.n:
            raise IOError("Face format is clashed")
        self.indices[1], self.indices[-1] = self.indices[-1], self.indices[1]
        if material is None:
            self.material = -1
        else:
            self.material = int(material)
        if uv is None or self.material == -1:
            self.uv = None
        else:
            self.uv = [float(i) for i in uv.split()]
            if len(self.uv) != self.n*2:
                raise IOError("Face format is clashed")
            self.uv[2], self.uv[-2] = self.uv[-2], self.uv[2]
            self.uv[3], self.uv[-1] = self.uv[-1], self.uv[3]
            for i in range(1, self.n*2, 2):
                self.uv[i] = 1.0 - self.uv[i]
        self.make_hash()

    def make_hash(self):
        self.h = hash(tuple(self.indices))

    def __eq__(self, othr):
        return self.h == othr.h and self.indices == othr.indices

    def mirror_copy(self, vertex, xi):
        face = Face()
        face.n = self.n
        face.material = self.material
        if self.uv:
            face.uv = self.uv[:]
            face.uv[2], face.uv[-2] = face.uv[-2], face.uv[2]
            face.uv[3], face.uv[-1] = face.uv[-1], face.uv[3]
        else:
            face.uv = None
        it = list(range(self.n))
        it[1], it[-1] = it[-1], it[1]
        face.indices = []
        c = 0
        for i in it:
            v = list(map(operator.mul, xi, vertex[self.indices[i]]))
            try:
                index = vertex.index(v)
            except ValueError:
                index = len(vertex)
                vertex.append(v)
                c += 1
            face.indices.append(index)
        face.make_hash()
        return face, c

class Material(object):
    __slots__ = ("color", "tex_name")
    def __init__(self):
        self.color = None
        self.tex_name = ""

    def __eq__(self, othr):
        return self.color == othr.color and self.tex_name == othr.tex_name

class Obj(object):

    def __init__(self):
        self.vertex = []
        self.faces  = []
        self.mirror = None
        self.mirror_axis = None

    def __iadd__(self, othr):
        vmap = [0]*len(othr.vertex)
        n = len(self.vertex)
        vs = []
        for i, v in enumerate(othr.vertex):
            try:
                vmap[i] = self.vertex.index(v)
            except ValueError:
                vmap[i] = n
                n += 1
                vs.append(v)
        self.vertex.extend(vs)

        fs = []
        for face in othr.faces:
            face.indices = [vmap[i] for i in face.indices]
            face.make_hash()
            if face not in self.faces:
                fs.append(face)
        self.faces.extend(fs)
        return self

    def expand_mirror(self):
        if self.mirror not in [None, 0] and self.mirror_axis is not None:
            x = y = z = 1.0
            if self.mirror_axis&1: x = -1.0
            if self.mirror_axis&2: y = -1.0
            if self.mirror_axis&4: z = -1.0
            xi = [x, y, z]
            fs = []
            for f in self.faces:
                ff, c = f.mirror_copy(self.vertex, xi)
                if c and ff in self.faces:
                    self.vertex = self.vertex[:-c]
                else:
                    fs.append(ff)
            self.faces.extend(fs)
            self.mirror = None

    def check_material_uv(self, materials, mmap):
        for face in self.faces:
            if face.material >= 0:
                mi = mmap[face.material]
                face.material = mi
                if not materials[mi].tex_name:
                    # マテリアルにテクスチャが設定されていない -> 面のUV座標を消す
                    face.uv = None
                elif face.uv is None:
                    # マテリアルにテクスチャが設定されているのに面にUV座標がない
                    # -> 新規に色のみのマテリアルを割り当てる
                    m = Material()
                    m.color = materials[mi].color
                    try:
                        face.material = materials.index(m)
                    except ValueError:
                        face.material = len(materials)
                        materials.append(m)
            else:
                # マテリアル無しはオブジェクトの色でマテリアルを新規作成
                face.uv = None
                m = Material()
                m.color = self.color
                try:
                    face.material = materials.index(m)
                except ValueError:
                    face.material = len(materials)
                    materials.append(m)

    def normalize(self, length=1.0, dy=-0.5):
        max_y = 0.0
        min_y = 0.0
        for x,y,z in self.vertex:
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y
        ly = max_y - min_y
        fact = length / ly
        self.vertex = [[x*fact, (y-min_y)*fact+dy, z*fact]
                        for x,y,z in self.vertex]

class MqoObject(object):

    re_chunk  = re.compile(r"^(\w+)\s*(\d+)?\s*{")
    re_object = re.compile(r'^Object\s*"([^"]+)"\s+{')
    re_face   = re.compile(r"""
                           ^(\w+)\s*              #1 頂点数
                           V\(([^)]*)\)\s*        #2 頂点インデックス
                           (?:M\(([^)]*)\))?\s*   #3 材質インデックス
                           (?:UV\(([^)]*)\))?\s*  #4 UV値
                           (?:COL\(([^)]*)\))?\s* #5 頂点カラー
                           """, re.VERBOSE)

    def __init__(self, imqo):
        self.imqo = imqo
        self.check_header()
        self.obj = Obj()
        materials = []
        try:
            while True:
                chunk = self.search_chunk().lower()
                if chunk == "object": # 複数あり
                    obj = self.object_chunk()
                    obj.expand_mirror()
                    self.obj += obj
                elif chunk == "material": # 1回
                    materials = self.material_chunk()
                else:
                    self.skip_chunk()
        except StopIteration:
            pass
        if not materials:
            raise IOError("Material-Chunk is essential")

        self.materials = []
        mmap = [0]*len(materials)
        for i, m in enumerate(materials):
            try:
                index = self.materials.index(m)
            except ValueError:
                index = len(self.materials)
                self.materials.append(m)
            mmap[i] = index
        self.obj.check_material_uv(self.materials, mmap)
        self.obj.normalize()

        def key(face):
            if face.uv is None:
                s = 1000000
            else:
                s = 0
            s += face.material
            return s
        self.obj.faces.sort(key=key)

    ###### read tool ######

    def check_header(self):
        firstline = next(self.imqo)
        if "Metasequoia Document" not in firstline:
            raise IOError("This file is not Metasequoia Document")

        line = next(self.imqo)
        m = re.match("^Format (\w+) Ver (\d+)\.(\d+)", line)
        if m:
            if m.group(1) != "Text":
                raise IOError("This file format is not supported")
            if m.group(2) != "1":
                raise IOError("This file version is not supported")
        else:
            raise IOError("This file format is not supported")

    def search_chunk(self):
        while True:
            line = next(self.imqo).strip()
            m = self.re_chunk.match(line)
            if m:
                return m.group(1)
            m = self.re_object.match(line)
            if m:
                return "object"

    def material_chunk(self):
        re_comp = re.compile(r"""
                             \s+
                             (?=
                                 \w+ # パラメータ
                                 \(
                                     [^)]* # 値
                                 \)
                             )
                             """, re.VERBOSE)
        re_field = re.compile("^(\w+)\(([^)]*)\)")
        materials = []
        while True:
            line = next(self.imqo).strip()
            if line == "}":break
            material = Material()
            fields = re_comp.split(line)
            for field in fields:
                m = re_field.match(field)
                if m:
                    if m.group(1) == "col":
                        material.color = [float(i)for i in m.group(2).split()]
                    elif m.group(1) == "tex":
                        material.tex_name = m.group(2)[1:-1]
            materials.append(material)
        return materials

    def object_chunk(self):
        obj = Obj()
        vertex = []
        while True:
            line = next(self.imqo).strip()
            if line == "}":break
            m = self.re_chunk.match(line)
            if m:
                chunk = m.group(1).lower()
                if chunk == "vertex":
                    vertex = self.vertex_chunk()
                elif chunk == "face":
                    obj.faces = self.face_chunk()
                else:
                    self.skip_chunk()
            else:
                fields = line.split()
                name = fields[0]
                if name == "mirror":
                    obj.mirror = int(fields[1])
                elif name == "mirror_axis":
                    obj.mirror_axis = int(fields[1])
                elif name == "color":
                    obj.color = [float(i) for i in fields[1:]]
                elif name == "scale":
                    obj.scale = [float(i) for i in fields[1:]]
                    if obj.scale != [1.0,1.0,1.0]:
                        print("s",obj.scale)
                elif name == "rotation":
                    obj.rotation = [float(i) for i in fields[1:]]
                    if obj.rotation != [.0,.0,.0]:
                        print("r",obj.rotation)
                elif name == "translation":
                    obj.translation = [float(i) for i in fields[1:]]
                    if obj.translation != [.0,.0,.0]:
                        print("t",obj.translation)

        vmap = [0]*len(vertex)
        for i, v in enumerate(vertex):
            try:
                vmap[i] = obj.vertex.index(v)
            except ValueError:
                vmap[i] = len(obj.vertex)
                obj.vertex.append(v)
        for face in obj.faces:
            face.indices = [vmap[i] for i in face.indices]

        return obj

    def vertex_chunk(self):
        vertex = []
        while True:
            line = next(self.imqo).strip()
            if line == "}":break
            v = list(map(float, line.split()))
            vertex.append(v)
        return vertex

    def face_chunk(self):
        faces = []
        while True:
            line = next(self.imqo).strip()
            if line == "}":break
            m = self.re_face.match(line)
            face = Face(*m.groups())
            if face.n != 0 and face not in faces:
                faces.append(face)
        return faces

    def skip_chunk(self):
        while True:
            line = next(self.imqo).strip()
            if line == "}":break
            if self.re_chunk.match(line):
                self.skip_chunk()


if __name__ == "__main__":
    import time, sys
    class F(object):
        def __init__(self, io):
            self.lis = io.readlines()
            self.n = len(self.lis)
            self.i = 0
            self.ii = 0
            print("-"*100)
        def __next__(self):
            if self.i < self.n:
                self.i += 1
                if self.i*100/self.n > self.ii:
                    sys.stdout.write("#")
                    sys.stdout.flush()
                    self.ii += 1
                return self.lis[self.i-1]
            else:
                print()
                raise StopIteration

    t1 = time.clock()
    name = "../resources/img/haruna/haruna.mqo"
    m = MqoObject(F(open(name)))
    t2 = time.clock()
    print(t2 - t1)
