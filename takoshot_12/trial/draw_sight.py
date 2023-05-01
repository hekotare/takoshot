import random

import globals as g
import graphics as gra
import graphics_ex as gra_ex
import main
from core.input_sys import KeyCodes
from core.scene import Scene


#
# パイ型、リング型の描画を使って
# レーダーっぽいものを描画してみる
#
# python -m trial.draw_sight を入力して実行
class Scene_TrySight(Scene):

    def __init__(self):
        super().__init__()
        
        self.target_degree = 0
        self.posture_degree = 0
        self.color_list = [(255, 255, 0),
                      (255, 255, 0),
                      (255, 255, 0),
                      (255, 255, 255)]
    
    def prepare(self):
        pass
    
    def update(self):
        pass
    
    def render(self):
        
        if (g.systems.input_sys.is_push(KeyCodes.C)):
            self.color_list = \
            [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) \
                for _ in range(4)]
        
        if (g.systems.input_sys.is_keydown(KeyCodes.LSHIFT)):
            if (g.systems.input_sys.is_keydown(KeyCodes.UP)):
                self.posture_degree += 1
            if (g.systems.input_sys.is_keydown(KeyCodes.DOWN)):
                self.posture_degree -= 1
        else:
            if (g.systems.input_sys.is_keydown(KeyCodes.UP)):
                self.target_degree -= 1
            if (g.systems.input_sys.is_keydown(KeyCodes.DOWN)):
                self.target_degree += 1
        
        #func = self.draw_sight
        func = gra_ex.draw_sight
        func(g.surface, 200, 200, 120, self.target_degree, -45, 45, self.posture_degree, self.color_list)
    
    @classmethod
    def draw_sight(cls, surface, x, y, radius, target_degree, min_degree, max_degree, posture_degree, color_list):
    
        color_0 = color_list[0]
        color_1 = color_list[1]
        color_2 = color_list[2]
        color_3 = color_list[3]
        space_value = 8
        
        # 照準をプレイヤーの姿勢分だけ回転させる
        target_degree -= posture_degree
        min_degree -= posture_degree
        max_degree -= posture_degree
        
        # 外枠
        for i in range(8):
            s = int(i/8 * 360)
            e = int((i + 1)/8 * 360)
            gra.ring(surface, x, y, radius, radius - 4, s, e, 20, fill=color_0, space_dot=space_value)
        
        # 内枠
        for i in range(16):
            s = int(i/16 * 360)
            e = int((i + 1)/16 * 360)
            gra.ring(surface, x, y, radius - 10, radius - 14, s, e, 20, fill=color_1, space_dot=space_value)
        
        # 射撃可能な範囲
        gra.pie(surface, x, y, radius - 20, min_degree, max_degree, 20, fill=color_2, space_dot=space_value)
        
        # 照準
        gra.pie(surface, x, y, radius, target_degree-2, target_degree+2, 4, fill=color_3)
        gra.ring(surface, x, y, radius + 10, radius + 4, target_degree-2, target_degree+2, 4, fill=color_3)


if __name__ == '__main__':
    main.main(Scene_TrySight())
