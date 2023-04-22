import math

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
        if (child.id == SceneId.MAINGAME_READYGO):
            self.add_child(Scene_ControlPlayer(self.get_next_active_player()))
        if (child.id == SceneId.MAINGAME_CONTROL_PLAYER):
            self.add_child(Scene_TurnEnd())
        if (child.id == SceneId.MAINGAME_TURN_END):
            self.add_child(Scene_ControlPlayer(self.get_next_active_player()))
    
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
        self.end_ms = g.systems.time_sys.get_sys_time_ms() + 1000
    
    def update(self):
        if (self.end_ms <= g.systems.time_sys.get_sys_time_ms()):
            self.end_scene()
    
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
         
        if (input_sys.is_keydown(KeyCodes.A)):
            cmd.move_left()
        if (input_sys.is_keydown(KeyCodes.D)):
            cmd.move_right()
    
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

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame(), window_width=1200)
