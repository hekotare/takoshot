import math
import pygame

class Geometry:
    
    def rotate(x, y, angle_radians):
    
        cos = math.cos(angle_radians)
        sin = math.sin(angle_radians)
        
        return (x * cos - y * sin, x * sin + y * cos)
    
    # ベクトル(0, -1)とベクトル(x, y)の角度を返す
    def vector_to_angle(x, y):
        return -pygame.math.Vector2(0, -1).angle_to(pygame.math.Vector2(x, y).normalize())
