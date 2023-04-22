import pygame

import globals as g
import graphics_ex as gra_ex
from defines import Dir
from entity.collision import Collision, Stage


class World:
    
    def __init__(self):
        self.player_list = []
        self.stage_surf = g.systems.res_sys.bitmap.get_bitmap('stage', 0).copy()
        self.stage = Stage(self.stage_surf)
        self.collision = Collision(self.stage)
    
    def add_player(self, x, y):
    
        p = Player(self, x, y)
        self.player_list.append(p)

        return  p
    
    def update(self):
        # player
        for player in self.player_list:
            player.update()
    
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
        def move_left(self):
            self.move = -1
        def move_right(self):
            self.move = 1

    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.dir = Dir.RIGHT
        self.posture_degree = 0
        self.foot_step = 0
        self.command = Player.Command()
    
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
        self.posture_degree = self.world.collision.calc_posture_degree(self.x, self.y, self.dir.is_right())
        
        cmd.reset()
    
    # プレイヤーの傾きから、描画用の回転値を取得する
    # プラスなら半時計周り、マイナスなら時計回りにする（pygame.transrate.rotateと同じにする）
    def posture_to_rotate_degree(self):
        return self.posture_degree * (1 if (self.dir.is_right()) else -1)
