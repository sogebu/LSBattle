#coding: utf8
#
# keys.py
#
import sdl2

from program.const import CONFIG_DIR


class Keys(object):
    config_fname = CONFIG_DIR+"keyconfig.ini"
    keymap_fname = CONFIG_DIR+"keymap.dat"
    def __init__(self):
        self.reset()
        self.default()
        self.load_config()

    def reset(self):
        self.k_accel = 0
        self.k_accel_priority = 0
        self.k_booster = 0
        self.k_turn_right = False
        self.k_turn_left = False
        self.k_turn_up = False
        self.k_turn_down = False
        self.k_turn_priority1 = 0
        self.k_turn_priority2 = 0
        self.k_bullet = 0
        self.k_look_behind = 0
        self.k_map = 1
        self.k_brake = 0

    def default(self):
        self.accel_forward = sdl2.SDLK_w
        self.accel_back    = sdl2.SDLK_s
        self.accel_right   = sdl2.SDLK_d
        self.accel_left    = sdl2.SDLK_a
        self.booster       = sdl2.SDLK_f
        self.brake         = sdl2.SDLK_r
        self.turn_right    = sdl2.SDLK_RIGHT
        self.turn_left     = sdl2.SDLK_LEFT
        self.turn_up       = sdl2.SDLK_UP
        self.turn_down     = sdl2.SDLK_DOWN
        self.shoot         = sdl2.SDLK_SPACE
        self.change_gun    = sdl2.SDLK_v
        self.toggle_HUD    = sdl2.SDLK_TAB
        self.names = ["accel_forward",
                      "accel_back",
                      "accel_right",
                      "accel_left",
                      "turn_right",
                      "turn_left",
                      "turn_up",
                      "turn_down",
                      "shoot",
                      "booster",
                      "brake",
                      "change_gun",
                      "toggle_HUD"]
        # self.name2 = ["Accel Forward ",
        #               "Accel Backward",
        #               "Accel Right   ",
        #               "Accel Left    ",
        #               "Booster       ",
        #               "brake         ",
        #               "Turn Right    ",
        #               "Turn Left     ",
        #               "Turn Up       ",
        #               "Turn Down     ",
        #               "Shoot         ",
        #               "Change Gun    ",
        #               "HUD ON/OFF    "]
        self.name2 = ["Accel Forward ",
                      "      Backward",
                      "      Right   ",
                      "      Left    ",
                      "Turn Right    ",
                      "     Left     ",
                      "     Up       ",
                      "     Down     ",
                      "Shoot         ",
                      "Booster       ",
                      "brake         ",
                      "Change Gun    ",
                      "HUD ON/OFF    "]

    def __iter__(self):
        for name in self.names:
            yield name, getattr(self, name)

    def load_config(self):
        try:
            f = open(self.config_fname)
            for line in f:
                name, value = line.split("=")
                if hasattr(self, name):
                    setattr(self, name, int(value))
        except IOError:
            self.save()
            return

    def load_map(self):
        self.key_map = {}
        try:
            f = open(self.keymap_fname)
            for line in f:
                name, value = line.split("=")
                self.key_map[int(value)] = name
        except IOError:
            for key in dir(sdl2):
                if key.startswith("SDLK_"):
                    self.key_map[getattr(sdl2, key)] = key[5:].upper()

    def save(self):
        f = open(self.config_fname, "w")
        for name in self.names:
            f.write("%s=%i\n"%(name, getattr(self, name)))
        f.close()


