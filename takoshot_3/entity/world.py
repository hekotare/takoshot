import pygame
import graphics_ex as gra_ex

class World:
    
    def __init__(self):
        self.player_list = []
        self.stage_surf = pygame.image.load('res/image/stage01.png').convert_alpha()
    
    def add_player(self, x, y):
    
        p = Player(self, x, y)
        self.player_list.append(p)

        return  p
    
    def update(self):
        # player
        for player in self.player_list:
            player.update()
    
    def render(self):
        gra_ex.draw_stage(self.stage_surf)

        for player in self.player_list:
            gra_ex.draw_player(player)

class Player:

    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.surf = pygame.image.load('res/image/chr01.png').convert_alpha()
    
    def update(self):
        pass