import math
import random

import pygame

import globals as g
import graphics_ex as gra_ex
from defines import (MAX_SHOT_VELOCITY, SHOT_COMMAND_LIST, STAGE_SKY_HEIGHT,
                     Dir, ShellType, clamp, play_se)
from entity.collision import Collision, Stage
from entity.effect import Particle, Particle2
from entity.shell import Shell
from geometry import Geometry


class World:
    
    def __init__(self, stage_id = 0):
        self.player_list = []
        self.shell_list  = []
        self.effect_list = []
        img = g.systems.res_sys.stage.bitmap(stage_id)
        self.stage_surf = img.copy()
        self.stage = Stage(self.stage_surf, (0, STAGE_SKY_HEIGHT))
        self.collision = Collision(self.stage)
        self.windy = Windy()
        
        # 背景のパーティクルを30個作成
        world_rect = self.collision.world_rect()
        
        for _ in range(30):
            self.effect_list.append(Particle2(self, world_rect.x + world_rect.width * random.random(), world_rect.y + world_rect.height * random.random()))
    
    # あとで消す予定のメソッド
    def add_player(self, x, y):
        from defines import ChrType
        return self.add_player2(ChrType.ORANGE, x, y)
    
    def add_player2(self, chr_type, x, y):
    
        p = Player(self, chr_type, x, y, f"player_{len(self.player_list) + 1}")
        self.player_list.append(p)
        
        print(f"プレイヤーの生成 chr_type={chr_type} x,y={x},{y}")

        return  p

    def add_shell(self, shell_type, owner, x, y, velocity):
    
        shell = Shell.create_shell(shell_type, owner, self, x, y, velocity)
        self.shell_list.append(shell)

        print(f"弾の生成 : {shell_type}")

        return shell
    
    def add_particles(self, breaked_list):
    
        # パーティクルは最大で10個まで生成しておく
        for x, y, color in random.sample(breaked_list, min(len(breaked_list), 10)):
            particle = Particle(self, x, y, color)
            self.effect_list.append(particle)
    
    def update(self):
        # player update
        for player in self.player_list:
            player.update()

       # shell remove
        killed_shell_list = [shell for shell in self.shell_list if shell.is_kill()]
        for killed_shell in killed_shell_list:
            self.shell_list.remove(killed_shell)
        
        # shell update
        for shell in self.shell_list:
            shell.update()
        
        # effect
        for killed_p in [p for p in self.effect_list if p.is_kill()]:
            self.effect_list.remove(killed_p)
        
        for eff in self.effect_list:
            eff.update()
        
        #
        g.systems.time_sys.step_world_frame()
    
    def render(self):
        gra_ex.draw_stage(self.stage)

        for player in self.player_list:
            gra_ex.draw_player(player)

class Player:

    class Command:
        def __init__(self):
            self.reset()
        def reset(self):
            self.move = 0
            self.shooting_angle = 0
            self.shot = None
        
        def move_left(self):
            self.move = -1
        def move_right(self):
            self.move = 1
        def increase_shooting_angle(self):
            self.shooting_angle += 1
        def decrease_shooting_angle(self):
            self.shooting_angle -= 1
        
        # shell_type: debug用, フツーはプレイヤーが現在装備している弾を撃つので不要
        def set_shot(self, power, shell_type = None):
            assert 0 <= power <= 1.0, F"power={power}"
            
            self.shot = {'power': power, 'shell_type': shell_type }
        
        def has_shot(self):
            return self.shot is not None
    
    class State:
        ALIVE       = 0 # 生きてる
        DESTROYED   = 1 # 破壊された
        LOST        = 2 # 消滅
    
    class Inventory:

        ORIGIN_X = 20
        ORIGIN_Y = 340
        EXTENT   = 40
        
        # 順番がアイテムアイコンのビットマップインデックスと一致するようにしている
        ITEM_LIST = [ShellType.TAKOYAKI, ShellType.PLASMA, ShellType.BIG_TAKO, ShellType.WARP]
        
        def __init__(self):
            self.items = []
            self.selected_index = 0
            self.x = self.ORIGIN_X
            self.y = self.ORIGIN_Y
        
        def add_item(self, item_type):
            assert item_type in self.ITEM_LIST, "item_type=" + str(item_type)
            
            self.items.append(item_type)

        def get_selected_item(self):
            return self.items[self.selected_index]
        
        def get_item_index_list(self):
            return [self.ITEM_LIST.index(item) for item in self.items]
        
        # 選択されているアイテムを消費する
        def consume(self):
            if (self.selected_index != 0):
                self.items.pop(self.selected_index)
                self.selected_index = 0
        
        def check_click_item(self, click_x, click_y):
            
            x = self.x
            
            for i, _ in enumerate(self.items):
                
                if (pygame.Rect(x, self.y, self.EXTENT, self.EXTENT).collidepoint(click_x, click_y)):
                    self.selected_index = i
                    play_se(g.systems, "se_inventory_push_item")
                    break
                
                x += self.EXTENT
        
        def draw(self):
            gra_ex.draw_inventory((self.x, self.y), self.EXTENT, self)
    
    def __init__(self, world, chr_type, x, y, player_name):
        self.world = world
        self.state = Player.State.ALIVE
        self.chr_type = chr_type
        self.x = x
        self.y = y
        self.is_land = False
        self.player_name = player_name
        self.hp = self.hp_max = 100
        self.move_energy = self.move_energy_max = 100
        self.dir = Dir.RIGHT
        self.posture_degree = 0
        self.foot_step = 0
        self.command = Player.Command()
        self.shooting_angle_min = 10
        self.shooting_angle_max = 70
        self.shooting_angle = 30
        self.muzzle_ofs_x, self.muzzle_ofs_y = (10, -20) # 銃口の座標（キャラの中心座標からのオフセット値）
        self.shot_timer = g.systems.time_sys.create_world_timer()
        self.shot_command = ShotCommand()

        self.inventory = Player.Inventory()
        self.inventory.add_item(ShellType.TAKOYAKI) # index=0の弾は基本装備であり、消滅しない
        self.inventory.add_item(ShellType.WARP)
        self.inventory.add_item(ShellType.BIG_TAKO)
        self.inventory.add_item(ShellType.PLASMA)
        
        self.ex_prop = {}
    
    def update(self):
        cmd = self.command

        if (self.shot_timer.enabled()):
            self.shot_command.process(self.world, self.shot_timer.progress, self, self.get_muzzle_position())
            
            if (self.shot_timer.is_finished()):
                self.shot_timer.clear()
        
        else:
            if cmd.has_shot():
                shot_power = cmd.shot['power']
                shell_type = self.inventory.get_selected_item()
                if cmd.shot['shell_type'] is not None: shell_type = cmd.shot['shell_type'] # テスト用
                self.inventory.consume() # 弾を消費

                self.shot_command.set(shell_type, self.calc_shooting_vector(shot_power * MAX_SHOT_VELOCITY))
                self.shot_timer.start(1000)
        
        move_x = self.command.move
        move_y = 5 # 重力の発生
        
        # update dir
        if (move_x < 0):
            self.dir = Dir.LEFT
        elif (0 < move_x):
            self.dir = Dir.RIGHT
        
        result = self.world.collision.intersect_ground_and_player(self.x, self.y, move_x, move_y)
        
        diff_x = self.x - result.x
        # 左右に移動できたら
        if (diff_x != 0):
            self.foot_step += abs(diff_x) 
        
        self.x, self.y = result.x, result.y
        self.is_land = result.is_land
        
        if (self.world.collision.check_player_lost(self.x, self.y)):
            self.state = Player.State.LOST
        
        self.shooting_angle = clamp(self.shooting_angle + cmd.shooting_angle, self.shooting_angle_min, self.shooting_angle_max)
        
        self.posture_degree = self.world.collision.calc_posture_degree(self.x, self.y, self.dir.is_right())
        self.posture_degree = round(self.posture_degree)
        
        cmd.reset()
    
    # プレイヤーの傾きから、描画用の回転値を取得する
    # プラスなら半時計周り、マイナスなら時計回り（pygame.transrate.rotateと同じ）
    def posture_to_rotate_degree(self):
        return self.posture_degree * self.dir.to_scalar()
    
    def is_alive(self):
        return self.state == Player.State.ALIVE

    def is_destoryed(self):
        return self.state == Player.State.DESTROYED

    def is_shooting(self):
        return self.is_alive() and self.shot_timer.enabled()
    
    def get_muzzle_position(self):
        x, y = Geometry.rotate(self.muzzle_ofs_x * self.dir.to_scalar(), 
                               self.muzzle_ofs_y, math.radians(-self.posture_degree) * self.dir.to_scalar())
        
        return int(self.x + x), int(self.y + y)
    
    def calc_shooting_vector(self, length = 1):
        v = pygame.math.Vector2((0, -1))
        v.rotate_ip((self.shooting_angle + -self.posture_degree) * self.dir.to_scalar())
        v.scale_to_length(length)
        
        return v
    
    def on_you_got_damage(self, damage):
    
        self.hp = clamp(self.hp - damage, 0, self.hp_max)
        
        if (self.hp == 0):
            self.state = Player.State.DESTROYED
    
    def on_next_phase(self):
        # 弾を追加
        if ShellType.WARP not in self.inventory.items:
            self.inventory.add_item(ShellType.WARP)
        if ShellType.PLASMA not in self.inventory.items:
            self.inventory.add_item(ShellType.PLASMA)
        if ShellType.BIG_TAKO not in self.inventory.items:
            self.inventory.add_item(ShellType.BIG_TAKO)

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
            
            # SE
            if cmd.shell_type == ShellType.PLASMA:
                se_name = "se_shoot1"
            elif cmd.shell_type == ShellType.BIG_TAKO:
                se_name = "se_shoot2"
            else:
                se_name = "se_shoot"
            
            play_se(g.systems, se_name)

            self.list.pop(0)
    
    def has_command(self):
        return len(self.list) != 0

#　天候（風）
class Windy:
    
    def __init__(self):
        self.set_random_value()
    
    def time_passes(self):
        self.time -= 1
        
        return self.time <= 0
    
    def set_random_value(self):
        self.value = random.randint(-10, 10)
        self.time  = 6
    
    def add_value(self, val):
        self.value += val
        self.value = clamp(self.value, -10, 10)
    
    # 風の強さを取得（-1.0～1.0) 左側に暴風なら-1.0, 右側に暴風なら+1.0
    def get_scale(self):
        return clamp(self.value * 0.1, -1.0, 1.0)