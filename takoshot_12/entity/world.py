import math

import globals as g
import graphics_ex as gra_ex
from defines import Dir, clamp
from entity.collision import Collision, Stage
from geometry import Geometry


class World:
    
    def __init__(self):
        self.player_list = []
        self.stage_surf = g.systems.res_sys.bitmap.get_bitmap('stage', 0).copy()
        self.stage = Stage(self.stage_surf)
        self.collision = Collision(self.stage)
    
    def add_player(self, x, y):
    
        p = Player(self, x, y, f"player_{len(self.player_list)}")
        self.player_list.append(p)

        return  p
    
    def update(self):
        # player
        for player in self.player_list:
            player.update()
        
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
        
        def move_left(self):
            self.move = -1
        def move_right(self):
            self.move = 1
        def increase_shooting_angle(self):
            self.shooting_angle += 1
        def decrease_shooting_angle(self):
            self.shooting_angle -= 1
    
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
        self.dir = Dir.RIGHT
        self.posture_degree = 0
        self.foot_step = 0
        self.command = Player.Command()
        self.shooting_angle_min = 10
        self.shooting_angle_max = 70
        self.shooting_angle = 30
        self.muzzle_ofs_x, self.muzzle_ofs_y = (10, -20) # 銃口の座標（キャラの中心座標からのオフセット値）
    
    def update(self):
        cmd = self.command
        
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
    # プラスなら半時計周り、マイナスなら時計回りにする（pygame.transrate.rotateと同じにする）
    def posture_to_rotate_degree(self):
        return self.posture_degree * (1 if (self.dir.is_right()) else -1)
    
    def is_alive(self):
        return self.state == Player.State.ALIVE

    def get_muzzle_position(self):
        x, y = Geometry.rotate(self.muzzle_ofs_x * self.dir.to_scalar(), 
                               self.muzzle_ofs_y, math.radians(-self.posture_degree) * self.dir.to_scalar())
        
        return int(self.x + x), int(self.y + y)