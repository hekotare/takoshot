import math

import pygame

import globals as g
import graphics_ex as gra_ex
from core.input_sys import KeyCodes
from core.scene import Scene, Scene_Container
from defines import MouseTargetId, SceneId, StageId
from game import Game


# python -m scene.maingame を入力し実行
# python -m debugpy --wait-for-client --listen 5678 scene/maingame.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_MainGame(Scene_Container):
    
    SHOTBAR_RECT = pygame.Rect(20, 540, 600, 20)

    def __init__(self):
        super().__init__(SceneId.MAINGAME)
    
    def prepare(self):
        self.game = Game()
        self.game.load(StageId.TRAINING)
        self.next_player_index = 0
        self.shotpower_rate = 0

        self.add_child(Scene_Intro(self))
    
    def on_update(self):
        input_sys = g.systems.input_sys

        if(input_sys.is_push(KeyCodes.F1)):
            self.add_child(Scene_Pause(SceneId.MAINGAME_PAUSE))
            return
        
        self.game.update()
    
    def on_render(self):
        g.graphics.fill((128, 128, 255))
        self.game.render()
        
        #---------------------------------------
        # UIの描画
        #---------------------------------------
        # 背景
        gra_ex.draw_ui_background()
        
        # SKIP, EXITボタンの描画
        w, h = 80, 32
        gra_ex.draw_button(420, 492, w, h, "SKIP", MouseTargetId.SKIP_BTN)
        gra_ex.draw_button(520, 492, w, h, "EXIT", MouseTargetId.EXIT_BTN)
        
        gra_ex.draw_shotbar(self.SHOTBAR_RECT, self.shotpower_rate, 0, 0, -1) #self.tri0_pos, self.tri1_pos, -1)

    def on_end_child_scene(self, child):
    
        if (child.id == SceneId.MAINGAME_INTRO):
            self.add_child(Scene_ReadyGo())
        elif (child.id == SceneId.MAINGAME_READYGO):
            if (not self.try_scene_game_result()):
                self.add_child(Scene_ControlPlayer(self, self.get_next_active_player()))
        elif (child.id == SceneId.MAINGAME_CONTROL_PLAYER):
            if child.has_result_ok(): # ショットあり
                self.add_child(Scene_WaitLandingShell(self, child.player))
            else:
                self.add_child(Scene_TurnEnd())
        elif (child.id == SceneId.MAINGAME_WAIT_LANDING_SHELL):
            self.add_child(Scene_TurnEnd())
        elif (child.id == SceneId.MAINGAME_TURN_END):
            if (not self.try_scene_game_result()):
                self.add_child(Scene_ControlPlayer(self, self.get_next_active_player()))
        elif (child.id == SceneId.MAINGAME_RESULT):
            self.end_scene() # メインゲームの終了
        elif (child.id == SceneId.MAINGAME_PAUSE):
            pass
        else:
            assert False, "謎のシーン"
    
    # 試合が決着しているか判定し、ゲーム結果画面に移行する
    def try_scene_game_result(self):
        
        finished, alive_players = self.game.check_game_finished()

        if (finished):
            self.add_child(Scene_GameResult(alive_players))
            return True
        
        return False

    def get_next_active_player(self):
    
        players = self.game.world.player_list
        
        player = players[self.next_player_index]
        self.next_player_index = (self.next_player_index + 1) % len(players)
        
        return player
    
    def set_shotpower_rate(self, shotpower_rate):
        self.shotpower_rate = shotpower_rate

# 戦いの前にすべてのプレイヤーを順番にカメラで写す
class Scene_Intro(Scene):
    def __init__(self, parent_scene):
        super().__init__(SceneId.MAINGAME_INTRO)
        self.parent_scene = parent_scene
    
    def prepare(self):
        self.parent_scene.game.cameraman.start_intro()
    
    def dispose(self):
        self.parent_scene.game.cameraman.end_intro()
    
    def update(self):
        if (self.parent_scene.game.cameraman.is_intro_finished()):
            self.end_scene()
    
    def is_exclusive(self):
        return False

# 画面にReady Go!!を表示
class Scene_ReadyGo(Scene):
    def __init__(self):
        super().__init__(SceneId.MAINGAME_READYGO)
    
    def prepare(self):
        self.timer = g.systems.time_sys.create_world_timer()
        self.timer.start(2000)
    
    def update(self):
        if (self.timer.is_finished()):
            self.end_scene()
    
    def render(self):
        y = g.BATTLE_SCREEN_RECT.top + g.BATTLE_SCREEN_RECT.height * 0.2
        
        if self.timer.progress < 0.5:
            # ready
            g.graphics.text((g.BATTLE_SCREEN_RECT.centerx, y), "Ready", (255, 255, 255), font=g.font_i40, textalign='center', shadow_color=(0, 0, 0))
        else:
            # go
            g.graphics.text((g.BATTLE_SCREEN_RECT.centerx, y), "Go!!", (255, 255, 255), font=g.font_i40, textalign='center', shadow_color=(0, 0, 0))
    
    def is_exclusive(self):
        return False

# プレイヤーの操作
class Scene_ControlPlayer(Scene):

    def __init__(self, parent_scene, player):
        super().__init__(SceneId.MAINGAME_CONTROL_PLAYER)
        
        self.parent_scene = parent_scene
        self.player = player
        self.shooting_timer = g.systems.time_sys.create_world_timer()
    
    def prepare(self):
        self.parent_scene.game.open_sight(self.player)

        # 現在アクティブなプレイヤーをカメラターゲットにする
        self.parent_scene.game.cameraman.set_target_entity(self.player)

    def dispose(self):
        self.parent_scene.game.close_sight()
    
    def update(self):
        input_sys = g.systems.input_sys
        
        if (input_sys.is_push(KeyCodes.ESC)):
            self.end_scene(self.Result.CANCEL)
            return
        
        if (self.player.is_alive()):
        
            if (self.shooting_timer.enabled()):
                if (self.control_shot()):
                    self.end_scene(self.Result.OK)
            else:
                self.control_move()
        else:
            # プレイヤーが操作中にやられた
            self.end_scene(self.Result.CANCEL)
        
        shot_power_rate = self.shooting_timer.progress if self.shooting_timer.enabled() else 0
        self.parent_scene.set_shotpower_rate(shot_power_rate)
    
    def control_move(self):
        input_sys = g.systems.input_sys
        cmd = self.player.command

        if (input_sys.is_keydown(KeyCodes.W)):
            cmd.decrease_shooting_angle()
        if (input_sys.is_keydown(KeyCodes.S)):
            cmd.increase_shooting_angle()
        if (input_sys.is_push(KeyCodes.SPACE)):
            self.shooting_timer.start(3000)
            return
        if (input_sys.is_keydown(KeyCodes.A)):
            cmd.move_left()
        if (input_sys.is_keydown(KeyCodes.D)):
            cmd.move_right()
    
    def control_shot(self):
        input_sys = g.systems.input_sys
        cmd = self.player.command

        if (input_sys.is_keyup(KeyCodes.SPACE) or self.shooting_timer.is_finished()):
            cmd.set_shot(self.shooting_timer.progress)
            return True
        if (input_sys.is_keydown(KeyCodes.W)):
            cmd.decrease_shooting_angle()
        if (input_sys.is_keydown(KeyCodes.S)):
            cmd.increase_shooting_angle()
        return False
    
    def is_exclusive(self):
        return False

# 弾が発射されて着弾を待つ
class Scene_WaitLandingShell(Scene):
    
    # player  弾を撃ったプレイヤー
    def __init__(self, parent_scene, player):
        super().__init__(SceneId.MAINGAME_WAIT_LANDING_SHELL)
        
        self.parent_scene = parent_scene
        self.player = player
        self.state = 0
    
    def prepare(self):
        pass
    
    def update(self):

        world = self.parent_scene.game.world
        
        # カメラを弾に向ける（ターゲット状態が維持されている場合は、プレイヤーから弾にカメラターゲットを移す）
        if (len(world.shell_list) != 0):
            self.parent_scene.game.cameraman.passive_target_entity(world.shell_list[0], 0.95)
        
        # まずはプレイヤーの射撃開始を待つ
        if (self.state == 0):
            # プレイヤーが射撃中 or プレイヤーが死亡 したら次へ
            if (self.player.is_shooting() or not self.player.is_alive()):
                self.state = 1
        elif (self.state == 1): # プレイヤーの射撃終了を待つ
            # プレイヤーの射撃が終了し、ワールド内に弾が存在しない
            if (not self.player.is_shooting() and len(world.shell_list) == 0):
                self.end_scene()

    def is_exclusive(self):
        return False

# ターンの終了
class Scene_TurnEnd(Scene):
    def __init__(self):
        super().__init__(SceneId.MAINGAME_TURN_END)
    
    def prepare(self):
        self.timer = g.systems.time_sys.create_world_timer()
        self.timer.start(1000)
    
    def update(self):
        if (self.timer.is_finished()):
            self.end_scene()
    
    def is_exclusive(self):
        return False

# ゲーム結果
class Scene_GameResult(Scene):

    def __init__(self, winner_players):
        super().__init__(SceneId.MAINGAME_RESULT)
        
        self.winner_players = winner_players
    
    def prepare(self):
        self.timer = g.systems.time_sys.create_world_timer()
        self.timer.start(2000)
    
    def update(self):
        if (self.timer.is_finished()):
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

class Scene_Pause(Scene):

    def update(self):
        if (g.systems.input_sys.is_push(KeyCodes.F1)):
            self.end_scene()

    def render(self):
        rect = pygame.Rect(100, 100, g.BATTLE_SCREEN_RECT.width - 200, g.BATTLE_SCREEN_RECT.height - 200)
        gra_ex.draw_window(rect, (100, 100, 100))

        g.graphics.text((rect.centerx, rect.top + rect.height * 0.4), "Pause", (255, 255, 255), textalign="center", font = g.font_i40, shadow_color=(0, 0, 0))

    def is_exclusive(self):
        return True

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame(), window_width=1200)
