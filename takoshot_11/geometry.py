import math

class Geometry:
    
    def rotate(x, y, angle_radians):
    
        cos = math.cos(angle_radians)
        sin = math.sin(angle_radians)
        
        return (x * cos - y * sin, x * sin + y * cos)
