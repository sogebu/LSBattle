#coding: utf8
import sdl2

from program.box import BOX
from program.text import MyFont
from sequence.locals import GameLevel, GameScore, backimage
from sequence.title import Title
from sequence.play import Play
from sequence.option import Option
from sequence.loading import Loading
from sequence.continequestion import ContineQuestion
from sequence.showscore import ShowScore
from sequence.entryhighscore import EntryHighScore
from sequence.showhighscore import ShowHighScore
from sequence.gameover import GameOver
from entity import PlayerState
from program import script


class Game(object):
    
    def __init__(self):
        BOX.game_init()
        BOX.resize(script.game.scale)
        backimage.load()
        MyFont.init_font(script.ui.font.name)
        
    def mainloop(self):
        title = Title()
        option = Option()
        top = True
        while True:
            flg = title.mainloop(top)
            if flg == title.PLAY:
                self.play_loop()
                top = True
            elif flg == title.OPTION:
                option.mainloop()
                top = False
            elif flg == title.RANKING:
                ranking = ShowHighScore.ranking()
                ranking.mainloop()
                top = False
            elif flg == title.QUIT:
                BOX.game_quit()
    
    def play_loop(self):
        loading = Loading()
        continue_q = ContineQuestion()
        gameover = GameOver()
        
        stage = 1
        total_score = 0
        playerstate = PlayerState()
        item = None
        while True:

            if item is None and playerstate.gun_num < playerstate.max_gun_num:
                gun = script.player.gun[playerstate.gun_num]
                if stage >= gun.stage_condition:
                    item = playerstate.gun_num

            sdl2.SDL_ShowCursor(0)
            loading.draw()
            # 1 game unit = scale * (ligh speed * 1 second)
            playerstate.reset_hp()
            play = Play(playerstate,
                        GameLevel(stage),
                        scale=script.game.scale,
                        total_score=total_score,
                        item=item)
            flg = play.mainloop()
            sdl2.SDL_ShowCursor(1)
            total_score = play.world.score
            if flg == play.WIN:
                score_object = GameScore(play.world, stage)
                total_score += score_object.get_total_score()
                showscore = ShowScore(score_object)
                flg = showscore.mainloop()
                if stage == script.game.stage_num or flg == showscore.TITLE:
                    if stage == script.game.stage_num:
                        gameover.mainloop(False)
                    else:
                        gameover.mainloop()
                    hs = EntryHighScore(total_score)
                    hs.mainloop()
                    break
                    
                stage += 1
                
                if item is not None and item < playerstate.gun_num:
                    item = None

                if item is None and playerstate.gun_num < playerstate.max_gun_num:
                    gun = script.player.gun[playerstate.gun_num]
                    if score_object.accuracy >= gun.accuracy_condition:
                        item = playerstate.gun_num

            elif flg == play.LOSE:
                playerstate.hp = script.player.hp
                if continue_q.n == script.game.continue_num or continue_q.mainloop() == continue_q.NO:
                    gameover.mainloop()
                    hs = EntryHighScore(total_score)
                    hs.mainloop()
                    break

            elif flg == play.ELSE:
                break
                
            else:
                raise