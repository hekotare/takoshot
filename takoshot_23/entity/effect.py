import random

import pygame

import globals as g
import graphics_ex as gra_ex


# 地形を壊したときのパーティクル
class Particle:

    def __init__(self, world, x, y, color):
        self.world = world
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = random.random() * 10.0 - 5
        self.velocity_y = random.random() * -5.0 - 5
        self.kill = False
    
    def is_kill(self):
        return self.kill
    
    def update(self):
        
        if (self.kill): return
        
        self.x += int(self.velocity_x)
        self.y += int(self.velocity_y)
        self.velocity_x = self.velocity_x * 0.996 #
        self.velocity_y = self.velocity_y + 0.250 #
        
        collision = self.world.collision
        
        if (not collision.is_world_range(self.x, self.y) or 
                (0.0 < self.velocity_y and collision.stage.is_block(self.x, self.y))):
            self.kill = True
    
    def render(self, game):
        gra_ex.draw_particle(g.surface, game.transform, self)

# 背景に降り注ぐ何か
class Particle2:

    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.alpha = 0
        self.radius = int(random.random() * 4) * 2 + 2
        self.velocity_y = 0.5 / self.radius + 1.0
        self.kill = False
        self.ms = random.random() * 5000
    
    def is_kill(self):
        return self.kill
    
    def update(self):
        
        #self.x += self.world.windy.get_scale()
        self.y += self.velocity_y
        self.alpha = g.systems.time_sys.cos_wave(5000, self.ms)
        self.alpha = (self.alpha + 1) / 2 # 0.0～1.0
        
        world_rect = self.world.collision.world_rect()
        
        if ((self.x + 50) < world_rect.left):
            self.x = world_rect.right + 50
        if (world_rect.right < (self.x - 50)):
            self.x = world_rect.left - 50
        
        if (world_rect.bottom < (self.y - 50)):
            self.y = world_rect.top - 50
    
    def render(self, game):
        gra_ex.draw_particle2(game.transform, self)
