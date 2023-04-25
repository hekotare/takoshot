import math

import pygame

import globals as g
import graphics_ex as gra_ex
from core.input_sys import KeyCodes
from core.scene import Scene, Scene_Container
from defines import SceneId
from entity.world import World


# python -m trial.maingame を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/maingame.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_MainGame(Scene_Container):

    def __init__(self):
        super().__init__(SceneId.MAINGAME)
    
    def prepare(self):
        self.world = World()
        self.world.add_player(140, 150)
        self.world.add_player(340, 150)
        self.next_player_index = 0
        
        self.add_child(Scene_Intro())
    
    def on_update(self):
        self.world.update()
    
    def on_render(self):
        g.graphics.fill((128, 128, 255))
        self.world.render()

        gra_ex.draw_scene_id(self)
    
    def on_end_child_scene(self, child):
    
        if (child.id == SceneId.MAINGAME_INTRO):
            self.add_child(Scene_ReadyGo())
        elif (child.id == SceneId.MAINGAME_READYGO):
            if (not self.try_scene_game_result()):
                self.add_child(Scene_ControlPlayer(self.get_next_active_player()))
        elif (child.id == SceneId.MAINGAME_CONTROL_PLAYER):
            self.add_child(Scene_TurnEnd())
        elif (child.id == SceneId.MAINGAME_TURN_END):
            if (not self.try_scene_game_result()):
                self.add_child(Scene_ControlPlayer(self.get_next_active_player()))
        elif (child.id == SceneId.MAINGAME_RESULT):
            self.end_scene() # メインゲームの終了
        else:
            assert False, "謎のシーン"
    
    # 試合が決着しているか判定し、ゲーム結果画面に移行する
    def try_scene_game_result(self):
    
        # 生存者チェック
        alive_players = [player for player in self.world.player_list if player.is_alive()]
        num_of_alive = len(alive_players)
        
        if (num_of_alive in [0, 1]): # 全員死亡した or 一人が生き残った
            self.add_child(Scene_GameResult(alive_players))
            return True
        
        return False

    def get_next_active_player(self):
    
        players = self.world.player_list
        
        player = players[self.next_player_index]
        self.next_player_index = (self.next_player_index + 1) % len(players)
        
        return player

# 戦いの前にすべてのプレイヤーを順番にカメラで写す
class Scene_Intro(Scene):
    def __init__(self):
        super().__init__(SceneId.MAINGAME_INTRO)
    
    def prepare(self):
        self.end_ms = g.systems.time_sys.get_sys_time_ms() + 1000
    
    def update(self):
        if (self.end_ms <= g.systems.time_sys.get_sys_time_ms()):
            self.end_scene()
    
    def is_exclusive(self):
        return False

# 画面にReady Go!!を表示
class Scene_ReadyGo(Scene):
    def __init__(self):
        super().__init__(SceneId.MAINGAME_READYGO)
    
    def prepare(self):
        self.end_ms = g.systems.time_sys.get_sys_time_ms() + 2000
    
    def update(self):
        if (self.end_ms <= g.systems.time_sys.get_sys_time_ms()):
            self.end_scene()
    
    def render(self):
        y = g.BATTLE_SCREEN_RECT.top + g.BATTLE_SCREEN_RECT.height * 0.2
        
        if (1000 <= (self.end_ms - g.systems.time_sys.get_sys_time_ms())):
            # ready
            g.graphics.text((g.BATTLE_SCREEN_RECT.centerx, y), "Ready", (255, 255, 255), font=g.font_i40, textalign='center', shadow_color=(0, 0, 0))
        else:
            # go
            g.graphics.text((g.BATTLE_SCREEN_RECT.centerx, y), "Go!!", (255, 255, 255), font=g.font_i40, textalign='center', shadow_color=(0, 0, 0))
    
    def is_exclusive(self):
        return False

# プレイヤーの操作
class Scene_ControlPlayer(Scene):
    def __init__(self, player):
        super().__init__(SceneId.MAINGAME_CONTROL_PLAYER)
        
        self.player = player

    def update(self):
        cmd = self.player.command
        input_sys = g.systems.input_sys
        
        if (input_sys.is_push(KeyCodes.ESC)):
            self.end_scene()
            return
        
        if (self.player.is_alive()):
            if (input_sys.is_keydown(KeyCodes.A)):
                cmd.move_left()
            if (input_sys.is_keydown(KeyCodes.D)):
                cmd.move_right()
        else:
            # プレイヤーが操作中にやられた
            self.end_scene()
    
    def is_exclusive(self):
        return False

# ターンの終了
class Scene_TurnEnd(Scene):
    def __init__(self):
        super().__init__(SceneId.MAINGAME_TURN_END)
    
    def prepare(self):
        self.end_ms = g.systems.time_sys.get_sys_time_ms() + 1000
    
    def update(self):
        if (self.end_ms <= g.systems.time_sys.get_sys_time_ms()):
            self.end_scene()
    
    def is_exclusive(self):
        return False

# ゲーム結果
class Scene_GameResult(Scene):

    def __init__(self, winner_players):
        super().__init__(SceneId.MAINGAME_RESULT)
        
        self.winner_players = winner_players
    
    def prepare(self):
        self.end_ms = g.systems.time_sys.get_sys_time_ms() + 2000
    
    def update(self):
        if (self.end_ms <= g.systems.time_sys.get_sys_time_ms()):
            self.end_scene()
    
    def render(self):
    
        rect = pygame.Rect(100, 100, g.BATTLE_SCREEN_RECT.width - 200, g.BATTLE_SCREEN_RECT.height - 200)
        
        if (len(self.winner_players) != 0):
            text = "WIN"
            window_color = (0, 0, 192)
        else:
            text = "DRAW"
            window_color = (100, 100, 100)
        
        #g.graphics.rectangle(rect, fill=(32, 64, 128), outline=(20, 20, 20), width = 2)
        gra_ex.draw_window(rect, window_color)
        
        x = rect.centerx
        y = 120
        
        # ゲーム結果: WIN or DRAW
        g.graphics.text((x, y), text, (255, 255, 255), textalign="center", font = g.font_i40, shadow_color=(0, 0, 0))
        
        x = 140
        y += 80
        for player in self.winner_players:
            g.graphics.text((x + 30, y), player.player_name, (255, 255, 255), font = g.font_i40)
            y += 50

    def is_exclusive(self):
        return False

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame(), window_width=1200)
