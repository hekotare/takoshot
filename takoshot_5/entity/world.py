import pygame

import graphics_ex as gra_ex
from entity.collision import Collision, Stage


class World:
    
    def __init__(self):
        self.player_list = []
        self.stage_surf = pygame.image.load('res/image/stage01.png').convert_alpha()
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
        self.surf = pygame.image.load('res/image/chr01.png').convert_alpha()
        self.command = Player.Command()
    
    def update(self):
        cmd = self.command
        
        move_x = self.command.move
        move_y = 5 # 重力の発生 
        result = self.world.collision.intersect_ground_and_player(self.x, self.y, move_x, move_y)
        
        self.x, self.y = result.x, result.y

        cmd.reset()