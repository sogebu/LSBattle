#coding: utf8
# gamelevel.py
from program import script

EASY   = 0
NORMAL = 1
HARD   = 2
TRAVEL = 3


class GameLevel(object):
    def __init__(self, stage, mode):
        self.stage = stage
        self.mode = mode
        self.L = script.game.stage._colosseum_size(stage)
        self.stage_name = "STAGE %i"%stage if stage < script.game.stage_num else "LAST STAGE"
        self.enemy_num = script.game.stage._enemy_num(stage)
        self.types = script.game.stage._types_num(stage)

        self.table = {
            "accel_back": {EASY:False, NORMAL: True, HARD:True, TRAVEL:True},
            "booster": {EASY:False, NORMAL: False, HARD:True, TRAVEL:True},
            "accel_right": {EASY:False, NORMAL: True, HARD:True, TRAVEL:True},
            "accel_left": {EASY:False, NORMAL: True, HARD:True, TRAVEL:True},
            "change_gun": {EASY:False, NORMAL: True, HARD:True, TRAVEL:False},
            "brake": {EASY:False, NORMAL: False, HARD:True, TRAVEL:True},
            "toggle_HUD": {EASY:False, NORMAL: True, HARD:True, TRAVEL:True},
        }

    def enabled(self, key):
        if key in self.table:
            return self.table[key][self.mode]
        else:
            return True

    def is_easy(self):
        return EASY == self.mode
    def is_normal(self):
        return NORMAL == self.mode
    def is_hard(self):
        return HARD == self.mode
    def is_travel(self):
        return TRAVEL == self.mode
