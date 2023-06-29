import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from entity.collision import Collision


#
# 線を引くテスト
#
# python -m trial.collision_create_line を入力し実行
class Scene_TryLine(Scene):

    def __init__(self):
        super().__init__(g.systems)
        
        self.st_x = 0
        self.st_y = 0
        self.end_x = 4
        self.end_y = 15
    
    def prepare(self):
        pass
    
    def update(self):
        pass
    
    def render(self):

        scale = 24
        
        input = g.systems.input_sys
        x = int(input.mouse_pos[0] / scale)
        y = int(input.mouse_pos[1] / scale)
        
        if (input.is_push(KeyCodes.MOUSE_LEFT)):
            self.end_x, self.end_y = x, y
        elif (input.is_push(KeyCodes.MOUSE_RIGHT)):
            self.st_x, self.st_y = x, y
        
        if (input.is_keydown(KeyCodes.KEY_1)):
            point_list = self.bresenham(self.st_x, self.st_y, self.end_x, self.end_y)
        else:
            point_list = Collision.create_line(self.st_x, self.st_y, self.end_x, self.end_y)
        
        for point in point_list:
            x, y = point
            
            if (point == (self.st_x, self.st_y)):
                fill=(255, 128, 128); outline=(255, 255, 255)
                str = "S"
            elif (point == (self.end_x, self.end_y)):
                fill=(128, 255, 128); outline=(255, 255, 255)
                str = "E"
            else:
                fill=(192, 192, 192); outline=(255, 255, 255)
                str = ""
            
            g.graphics.rectangle((x * scale, y * scale, scale, scale),fill=fill, outline=outline, width=2)
            if (str): g.graphics.text((x * scale + 4, y * scale), str, (20, 20, 20))
    
    # ブレゼンハムのアルゴリズム（線を描く）
    def bresenham(self, st_x, st_y, end_x, end_y):
    
        point_list = []
        start = (st_x, st_y)
        end = (end_x, end_y)
        delta = (end_x - st_x, end_y - st_y)
        step = (1 if 0 < delta[0] else -1,
                1 if 0 < delta[1] else -1)
        delta = abs(delta[0]), abs(delta[1])
        
        fraction = 0
        current = [st_x, st_y]
        
        if (delta[0] > delta[1]):
        
            fraction = int(delta[1] - delta[0] * 0.5)
            
            while (current[0] != end[0]):
            
                point_list.append((current[0], current[1]))
                
                if (0 <= fraction):
                    current[1] += step[1]
                    fraction -= delta[0]
                
                current[0] += step[0]
                fraction += delta[1]
        
        else:
            
            fraction = int(delta[0] - delta[1] * 0.5)
            
            while (current[1] != end[1]):
            
                point_list.append((current[0], current[1]))
                
                if (0 <= fraction):
                    current[0] += step[0]
                    fraction -= delta[1]

                current[1] += step[1]
                fraction += delta[0]
        
        # 終点を含める
        point_list.append(end)
        
        return point_list

if __name__ == '__main__':
    main.main(Scene_TryLine, window_width=1200)
