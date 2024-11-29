#coding: utf8
import re
# import  logging

from .common import Block


class Parser(object):
    def __init__(self):
        self.re_block = re.compile(r"^(\w+)\s*{$")
        self.re_member = re.compile(r"^(\w+)\s*=\s*(.+)")
        self.n = 0

    def read(self):
        while True:
            self.n += 1
            line = next(self.f) + " "
            line = line[:line.find("#")].strip()
            if line and not line.startswith("#"):
                return line

    def parse(self, f, **setting):
        self.f = f
        self.n = 0
        self.setting = setting
        while True:
            try:
                line = self.read()
            except StopIteration:
                return
            m = self.re_block.match(line)
            if m is None:
                continue
            name = m.group(1)
            if name in self.setting:
                self.read_block(self.setting[name])
            else:
                self.skip_block()

    def perse_oneline_block(self, block, line):
        m = self.re_block.match(line)
        if m is None:
            return False
        name = m.group(1)
        if name.startswith("_"):
            return True
        if name in block:
            next_block = block[name]
            if "_"+name+"_obj" in block:
                self.read_list_block(block, name)
            elif isinstance(next_block, Block):
                self.read_block(next_block)
        else:
            self.skip_block()
        return True

    def perse_oneline_member(self, block, line):
        m = self.re_member.match(line)
        if m is None:
            return
        name, value = m.groups()
        if name.startswith("_"):
            return
        if name in block:
            if isinstance(block[name], Block):
                return
            func_name = "_"+name+"_func"
            if func_name in block:
                func = block[func_name]
                v = func(value)
                setattr(block, name, v)
            else:
                v = eval(value)
                setattr(block, name, v)

    def read_block(self, block):
        while True:
            line = self.read()
            if line == "}":return
            is_block = self.perse_oneline_block(block, line)
            if not is_block:
                self.perse_oneline_member(block, line)

    def read_list_block(self, block, name):
        block[name] = []
        obj_class = block["_"+name+"_obj"]
        while True:
            line = self.read()
            if line == "}":return
            m = self.re_block.match(line)
            if m is None:
                continue
            obj = obj_class()
            obj_name = m.group(1)
            if obj_name != obj.__class__.__name__:
                continue
            self.read_block(obj)
            block[name].append(obj)

    def skip_block(self):
        while True:
            line = self.read()
            if line == "}":return
            m = self.re_block.match(line)
            if m is not None:
                self.skip_block()


if __name__ == "__main__":
    f = open("ini")
    p = Parser()
    es = EnemySetting()
    p.parse(f, Enemy=es)
    print(es.character[0].name)
    print(es.character[0].HP)
    print(es.bullet.color)
