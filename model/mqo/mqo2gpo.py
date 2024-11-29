#coding: utf8
import os

from . import mqo_loader


class Point(object):
    def __init__(self, vertex, texcoord=None):
        self.vertex = vertex
        self.texcoord = texcoord

    def __eq__(self, othr):
        return (self.vertex == othr.vertex and self.texcoord == othr.texcoord)

    def __str__(self):
        s = "p %f %f %f "%tuple(self.vertex)
        if self.texcoord is not None:
            s += "%f %f"%tuple(self.texcoord)
        else:
            s += "0 0"
        return s


class Material(object):
    def __init__(self, m):
        self.color = m.color
        self.tex_name = m.tex_name

    def __str__(self):
        s = "m " + " ".join([str(c)for c in self.color])
        s += " \"" + self.tex_name + "\""
        return s

def output(name, points, objects):
    of = open(name+".gpo", "w")
    of.write("Game Polygon Object\n")
    for point in points:
        of.write(str(point) + "\n")
    for material, indices in objects:
        of.write(str(material) + "\n")
        of.write("i " + " ".join([str(i)for i in indices]) + "\n")
    of.close()

def mqo2gpo(name):
    mqo = mqo_loader.MqoObject(open(name))

    def _uv(i):
        index = face.indices[i]
        p = Point(mqo.obj.vertex[index], face.uv[i*2:i*2+2])
        if points[index] is None or points[index].texcoord is None:
            points[index] = p
        elif p.texcoord != points[index].texcoord:
            for k in range(pre_len, len(points)):
                if p == points[k]:
                    index = k
                    break
            else:
                index = len(points)
                points.append(p)
        return index
    def _col(i):
        index = face.indices[i]
        p = Point(mqo.obj.vertex[index])
        if points[index] is None:
            points[index] = p
        return index

    pre_len = len(mqo.obj.vertex)
    points = [None]*pre_len
    objects = []
    for num, face in enumerate(mqo.obj.faces):
        if num == 0 or face.material != mqo.obj.faces[num-1].material:
            objects.append([Material(mqo.materials[face.material]), []])
            indices = objects[-1][1]
        if face.uv is None:
            if face.n == 3:
                l = [_col(i) for i in (0,1,2)]
            else:
                l = [_col(i) for i in (0,1,2,3)]
                l = [l[i] for i in (0,1,2,0,2,3)]
        else:
            if face.n == 3:
                l = [_uv(i) for i in (0,1,2)]
            else:
                l = [_uv(i) for i in (0,1,2,3)]
                l = [l[i] for i in (0,1,2,0,2,3)]
        indices.extend(l)

    pmap = [0]*len(points)
    index = 0
    for i, p in enumerate(points):
        if p is None:
            continue
        pmap[i] = index
        index += 1
    for obj in objects:
        obj[1] = [pmap[i]for i in obj[1]]
    points = [p for p in points if p is not None]
    name, ext = os.path.splitext(name)
    output(name, points, objects)
