import pygame

import globals as g
import graphics_ex as gra_ex
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import SHOT_COMMAND_LIST, ShellType, clamp, float_format, StageId
from game import Game


# ワールドに弾を発生させて挙動やグラフィックをテストする
#
# python -m trial.shot_command を入力し実行
class Scene_TryShell(Scene):

    SHOT_BAR_RECT = (20, 480, 320, 20)

    def __init__(self):
        super().__init__()
    
    def prepare(self):
        self.game = Game()
        self.reset_game()
        self.shell_type_index = 0
        self.shell_type_list = ShellType.get_types()
    
    def reset_game(self):
        self.game.create_world(StageId.MOKUZAI)
        
        self.selected_player = self.game.world.add_player(200, 200)
        self.game.world.add_player(400, 100)
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
        x, y = input_sys.mouse_pos
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
            if (input_sys.is_push(KeyCodes.MOUSE_LEFT)):
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
            
            # shot power
            if (input_sys.is_keydown(KeyCodes.X)):
                self.shot_power_rate -= 0.02
            if (input_sys.is_keydown(KeyCodes.C)):
                self.shot_power_rate += 0.02
            self.shot_power_rate = clamp(self.shot_power_rate, 0.0, 1.0)
        else:
            # shot
            if (input_sys.is_push(KeyCodes.MOUSE_LEFT)):
                self.shot_command.set(self.get_shell_type(), (4, -8))
                self.muzzle_pos = (x, y)
                self.shot_timer.start(1000)
            if (input_sys.is_push(KeyCodes.MOUSE_RIGHT)):
                self.shot_command.set(self.get_shell_type(), (0, -8))
                self.muzzle_pos = (x, y)
                self.shot_timer.start(1000)
        
        if (input_sys.is_push(KeyCodes.Z)):
            self.shell_type_index = (self.shell_type_index + 1) % len(self.shell_type_list)
        
        self.game.update()
    
    def render(self):
    
        g.graphics.fill((160, 192, 255))
        self.game.render()

        gra_ex.draw_shotbar(pygame.Rect(self.SHOT_BAR_RECT), self.shot_power_rate, 0.0, 0.0)

        g.systems.debug_sys.text(f"shell_type={self.get_shell_type()}")
        
        # current mode
        g.systems.debug_sys.text(f"mode - {'Player Control Mode' if self.player_mode else 'ShotCommand Mode'} -")

        g.systems.debug_sys.text("- controls -")
        g.systems.debug_sys.text("KEY_1: reset game")
        g.systems.debug_sys.text("KEY_2: mode change")
        g.systems.debug_sys.text("KEY_Z: shell change")
        
        if self.player_mode:
            g.systems.debug_sys.text("W, A, S, D KEY: Player Move")
            g.systems.debug_sys.text("X, C KEY: Shot Power")
            g.systems.debug_sys.text("Left Click: Shot")
            g.systems.debug_sys.text("Right Click: Warp")
        else:
            g.systems.debug_sys.text(f"progress={float_format(self.shot_timer.progress)}")
    
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
    main.main(Scene_TryShell(), window_width=1200)
