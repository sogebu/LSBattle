# coding: utf8
# utils/shader.py
from OpenGL.GL import *


class ProgramInfo(object):
    def __init__(self, program_id, vertex_source, fragment_source, key):
        self.program_id = program_id
        self.vertex_source = vertex_source
        self.fragment_source = fragment_source
        self.key = key

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not status:
        s = glGetShaderInfoLog(shader)
        glDeleteShader(shader)
        raise ValueError("Shader compilation failed: %s"%s)
    return shader

_compiled_program = {}
_using_program_id = {}
def compile_program(vertex_source, fragment_source, cache=True):
    key = vertex_source + fragment_source
    if cache:
        program_info = _compiled_program.get(key)
        if program_info is not None and glIsProgram(program_info.program_id):
            return program_info.program_id

    vertex_shader   = compile_shader(vertex_source,   GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
    program_id = glCreateProgram()
    glAttachShader(program_id, vertex_shader)
    glAttachShader(program_id, fragment_shader)
    glLinkProgram(program_id)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    status = glGetProgramiv(program_id, GL_LINK_STATUS)
    if not status:
        s = glGetProgramInfoLog(program_id)
        raise ValueError("Program Link failed: %s"%s)

    program_info = ProgramInfo(program_id, vertex_source, fragment_source, key)
    if program_id in _using_program_id:
        deleted_key = _using_program_id[program_id].key
        del _compiled_program[deleted_key]
    _compiled_program[key] = program_info
    _using_program_id[program_id] = program_info

    return program_id
