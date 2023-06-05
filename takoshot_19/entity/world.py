import math
import random

import pygame

import globals as g
import graphics_ex as gra_ex
from defines import MAX_SHOT_VELOCITY, SHOT_COMMAND_LIST, Dir, ShellType, clamp
from entity.collision import Collision, Stage
from entity.effect import Particle, Particle2
from entity.shell import Shell
from geometry import Geometry


class World:
    
    def __init__(self, stage_id = 0):
        self.player_list = []
        self.shell_list  = []
        self.effect_list = []
        self.stage_surf = g.systems.res_sys.bitmap.get_bitmap('stage', stage_id).copy()
        self.stage = Stage(self.stage_surf)
        self.collision = Collision(self.stage)
        
        # 背景のパーティクルを30個作成
        world_rect = self.collision.world_rect()
        
        for _ in range(30):
            self.effect_list.append(Particle2(self, world_rect.x + world_rect.width * random.random(), world_rect.y + world_rect.height * random.random()))
    
    def add_player(self, x, y):
    
        p = Player(self, x, y, f"player_{len(self.player_list)}")
        self.player_list.append(p)
        
        print(f"プレイヤーの生成")

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

    def __init__(self, world, x, y, player_name):
        self.world = world
        self.state = Player.State.ALIVE
        self.x = x
        self.y = y
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
    
    def update(self):
        cmd = self.command

        if (self.shot_timer.enabled()):
            self.shot_command.process(self.world, self.shot_timer.progress, self, self.get_muzzle_position())
            
            if (self.shot_timer.is_finished()):
                self.shot_timer.clear()
        
        else:
            if cmd.has_shot():
                shot_power = cmd.shot['power']
                shell_type = cmd.shot['shell_type'] or ShellType.TAKOYAKI # Noneなら、とりあえずTAKOYAKIにしとく
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
        
        if (self.world.collision.check_player_lost(self.x, self.y)):
            self.state = Player.State.LOST
        
        self.shooting_angle = clamp(self.shooting_angle + cmd.shooting_angle, self.shooting_angle_min, self.shooting_angle_max)
        
        self.posture_degree = self.world.collision.calc_posture_degree(self.x, self.y, self.dir.is_right())
        
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