import pygame

import globals as g
import graphics_ex as gra_ex
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import (MAX_SHOT_VELOCITY, SHOT_COMMAND_LIST, ShellType, StageId,
                     clamp, float_format)
from game import Game


# ワールドに弾を発生させて挙動やグラフィックをテストする
#
# python -m trial.shot_command を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/shot_command.py を入力し、リモートデバッグ実行
class Scene_TryShell(Scene):

    SHOT_BAR_RECT = (20, 520, 320, 20)

    def __init__(self):
        super().__init__(g.systems)
    
    def prepare(self):
        self.game = Game()
        self.reset_game()
        self.shell_type_index = 0
        self.shell_type_list = ShellType.get_types()
        self.tri0_pos = 0
        self.tri1_pos = 0
        self.drag_event_obj = {}
    
    def reset_game(self):
        self.game.load(StageId.MOKUZAI)
        self.selected_player = self.game.world.player_list[0]

        self.game.cameraman.set_target_entity(self.selected_player)

        # ショット
        self.shot_timer = g.systems.time_sys.create_world_timer()
        self.shot_command = ShotCommand()
        self.muzzle_pos = (0, 0)
        self.shot_power_rate = 0.5
        self.old_shot_power_rate = -1

        self.player_mode = False
    
    def update(self):
    
        input_sys = g.systems.input_sys
        x, y = self.game.transform.screen_to_world(*input_sys.mouse_pos)
        x, y = int(x), int(y)
        
        if (self.shot_timer.enabled):
            self.shot_command.process(self.game.world, self.shot_timer.progress, self.selected_player, self.muzzle_pos)
        
        if (input_sys.is_push(KeyCodes.KEY_1)):
            self.reset_game()
            return
        if (input_sys.is_push(KeyCodes.KEY_2)):
            self.player_mode = not self.player_mode

            if (self.player_mode): self.game.open_sight(self.selected_player)
            else:                  self.game.close_sight()
        
        if self.player_mode:
        
            # player controls
            cmd = self.selected_player.command
            if (input_sys.is_push(KeyCodes.SPACE)):
                cmd.set_shot(self.shot_power_rate, self.get_shell_type()) # shot
            if (input_sys.is_keydown(KeyCodes.W)):
                cmd.decrease_shooting_angle()
            if (input_sys.is_keydown(KeyCodes.S)):
                cmd.increase_shooting_angle()
            if (input_sys.is_keydown(KeyCodes.A)):
                cmd.move_left()
            if (input_sys.is_keydown(KeyCodes.D)):
                cmd.move_right()
            
            # warp
            if (input_sys.is_push(KeyCodes.MOUSE_RIGHT)):
                self.selected_player.x = x
                self.selected_player.y = y
        
        else:
            # shot
            if (input_sys.is_push(KeyCodes.SPACE)):
                self.shot_command.set(self.get_shell_type(), (0, -MAX_SHOT_VELOCITY * self.shot_power_rate))
                self.muzzle_pos = (x, y)
                self.shot_timer.start(1000)
        
        # windy
        if (input_sys.is_push(KeyCodes.LEFT)):
            self.game.world.windy.add_value(-1)
        elif (input_sys.is_push(KeyCodes.RIGHT)):
            self.game.world.windy.add_value(1)
        
        # shot power
        if (input_sys.is_keydown(KeyCodes.DOWN)):
            self.shot_power_rate -= 0.02
        if (input_sys.is_keydown(KeyCodes.UP)):
            self.shot_power_rate += 0.02
        self.shot_power_rate = clamp(self.shot_power_rate, 0.0, 1.0)
             
        if (input_sys.is_push(KeyCodes.Z)):
            self.shell_type_index = (self.shell_type_index + 1) % len(self.shell_type_list)
        
        self.game.update()
    
    def render(self):
    
        g.graphics.fill((160, 192, 255))
        self.game.render()

        # ドラッグイベント
        # event_objに新しい値があったらtri0, tri1を更新
        if self.drag_event_obj.get('tri0_pos') is not None:
            self.tri0_pos = self.drag_event_obj['tri0_pos']
            del self.drag_event_obj['tri0_pos']
        if self.drag_event_obj.get('tri1_pos') is not None:
            self.tri1_pos = self.drag_event_obj['tri1_pos']
            del self.drag_event_obj['tri1_pos']
        
        gra_ex.draw_shotbar(pygame.Rect(self.SHOT_BAR_RECT), self.shot_power_rate, self.tri0_pos, self.tri1_pos, self.drag_event_obj)
        
        gra_ex.draw_windy(pygame.Rect(20, 380, 100, 20), self.game.world.windy)

        g.systems.debug_sys.text(f"shell_type={self.get_shell_type()}")
        
        g.systems.debug_sys.text("- controls -")
        g.systems.debug_sys.text("KEY_1: reset game")
        g.systems.debug_sys.text("KEY_2: mode change")
        g.systems.debug_sys.text("KEY_Z: shell change")
        
        g.systems.debug_sys.text("Space Key: Shot")
        g.systems.debug_sys.text("UP,DOWN KEY: Shot Power")
        g.systems.debug_sys.text("LEFT,RIGHT KEY: Wind")

        g.systems.debug_sys.text("--------------------")

        # current mode
        g.systems.debug_sys.text(f"mode - {'Player Control Mode' if self.player_mode else 'ShotCommand Mode'} -")
        
        if self.player_mode:
            g.systems.debug_sys.text("W, A, S, D KEY: Player Move")
            g.systems.debug_sys.text("Right Click: Warp")
        else:
            g.systems.debug_sys.text(f"progress={float_format(self.shot_timer.progress)}")
        
        gra_ex.draw_shell_airtime(self.game.world)
    
    def get_shell_type(self):
        return self.shell_type_list[self.shell_type_index]

class ShotCommand:

    class Cmd:
        def __init__(self, shell_type, cmd, velocity):
            self.shell_type = shell_type
            self.cmd = cmd
            self.velocity = velocity
    
    def __init__(self):
        self.list = []
    
    def set(self, shell_type, velocity):
    
        self.list = []

        cmd_list = SHOT_COMMAND_LIST.get(shell_type) or SHOT_COMMAND_LIST['default']
        
        for cmd in cmd_list:
            self.add_command(shell_type, cmd, velocity)
    
    def add_command(self, shell_type, cmd, velocity):
        self.list.append(ShotCommand.Cmd(shell_type, cmd, velocity))
    
    def process(self, world, progress, shooter, muzzle_pos):
    
        while(self.has_command()):
        
            cmd = self.list[0]
            time = cmd.cmd['time']
            
            if (progress <= time): break # まだコマンドを実行するタイミングではない
            
            # 射撃コマンドの実行
            world.add_shell(cmd.shell_type, shooter, *muzzle_pos, cmd.velocity)
            
            self.list.pop(0)
    
    def has_command(self):
        return len(self.list) != 0

if __name__ == '__main__':
    main.main(Scene_TryShell, window_width=1200)
