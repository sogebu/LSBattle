#coding: utf8
from program import script


class GameScore(object):
    def __init__(self, world, stage):
        self.stage  = stage
        self.p_time = world.player.time
        self.hp     = world.player.state.hp

        self.bullet_shoot = sum(gun.bullets.n for gun in world.player.guns)
        self.bullet_hit = sum(gun.bullets.hit_n for gun in world.player.guns)
        for gun in world.player.guns:
            for bullet in gun.bullets:
                if bullet.hit:
                    self.bullet_hit += 1
        self.accuracy = (self.bullet_hit+1)*1.0/(self.bullet_shoot+1)

    def get_score_list(self):
        s = self.stage**script.game.score.stage_power
        return [int(s*script.game.score.clear_time * (self.p_time+script.game.score.clear_time_geta)**script.game.score.clear_time_power),
                int(s*script.game.score.hp * (self.hp*1.0/script.player.hp)**script.game.score.hp_power),
                int(s*script.game.score.accuracy * self.accuracy**script.game.score.accuracy_power)]

    def get_total_score(self, lis=None):
        if lis is None:
            return sum(self.get_score_list())
        else:
            return sum(lis)

    def get_text(self):
        text1 = ["Proper time",
                 "HP",
                 "Accuracy",
                 "",
                 "Total"]
        text2 = ["%is"%self.p_time,
                 "%i"%self.hp,
                 "%i%%"%(self.accuracy*100),
                 "",
                 ""]
        text3 = "%i\n"*4
        score_lis = self.get_score_list()
        score_lis.append(self.get_total_score(score_lis))
        text3 = text3%tuple(score_lis)
        text3 = text3.split()
        text3.insert(-1, "")
        return text1, text2, text3
