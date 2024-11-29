#coding: utf8
import re


class Block(object):
    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def _check(self):
        for name in dir(self):
            if not name.startswith("_"):
                obj = getattr(self, name)
                if isinstance(obj, Block):
                    obj._check()


def color_func(line):
    if line == "None":
        return (1.0, 1.0, 1.0, 1.0)
    line = eval(line)[:4]
    color = []
    for c in line:
        c = float(c)
        if c < 0.0:
            color.append(0.0)
        elif c > 1.0:
            color.append(1.0)
        else:
            color.append(c)
    n = len(color)
    if n < 4:
        color += [1.0] * (4-n)
    return color

s_float = float
s_int   = lambda x:int(float(x))
_func_hash = {}
re_type = re.compile(r"<type (['\"])(\w+)\1>")
def high_func_num(func, m, M, none=False):
    key = (id(func), m, M, none)
    if key in _func_hash:
        return _func_hash[key]
    def f(line):
        if none and line == "None":
            return None
        value = func(line)
        if value < m:
            return m
        elif value > M:
            return M
        else:
            return value
    s = str(func if func is not s_int else int)
    match = re_type.match(s)
    if match:
        s = match.group(2)
    f.__name__ = "%s %s<=x<=%s"%(s, m, M)
    _func_hash[key] = f
    return f

def func_str(line):
    line = line.strip()
    if line == "None":
        return None
    return line.replace("\\n", "\n")


if __name__ == "__main__":
    class Test(Block):
        def __init__(self):
            self.a = 1
            self._a_func = int

    t = Test()
    t.b = 1
    print("a" in t)
    print("b" in t)
    print("_a_func" in t)
    print(t["a"])
