import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import clamp


#
# パイ型、リング型の描画をおためし
#
# python -m trial.draw_pie_ring を入力して実行
class Scene_TryPie(Scene):

    def __init__(self):
        super().__init__()
        self.mode = 0
        self.value = 0
    
    def prepare(self):
        pass
    
    def update(self):

        if (g.systems.input_sys.is_push(KeyCodes.KEY_1)):
            self.mode = (self.mode + 1) % 2
            self.value = 0
        
        # dot
        if (g.systems.input_sys.is_keydown(KeyCodes.Z)):
            self.value -= 1
        elif (g.systems.input_sys.is_keydown(KeyCodes.X)):
            self.value += 1
        self.value = clamp(self.value, 0, 360)
    
    def render(self):
    
        split = 20

        # パイ型の描画
        x, y = 100, 100
        g.graphics.pie(x, y, 60, 0, 45, split, outline=(255, 0, 0), fill=(255, 255, 255))

        # パイ型の描画
        x, y = 250, 100
        for i in range(8):
            s = int(i/8 * 360)
            e = int((i + 1)/8 * 360)
            g.graphics.pie(x, y, 60, s, e, split, outline=(255, 0, 0), fill=(255 * i/8, 0, 0))
        
        # 半円の描画
        x, y = 400, 100
        g.graphics.pie(x, y, 60, -90, 90, split, fill=(255, 0, 0))
        
        # リング型の描画
        x, y, radius = 250, 300, 120
        for i in range(8):
            s = int(i/8 * 360)
            e = int((i + 1)/8 * 360)
            
            if (self.mode == 0):
                g.graphics.ring(x, y, int(radius), int(radius * 0.4), s, e, 20, fill=(255 * (i/8), 255 * (i/8), 0), outline=(192, 192, 128), width=4, space_dot=self.value)
            elif (self.mode == 1):
                g.graphics.ring(x, y, int(radius), int(radius * 0.4), s, e, 20, fill=(255 * (i/8), 255 * (i/8), 0), outline=(192, 192, 128), width=4, space_degree=self.value)

        WHITE_COLOR = (255, 255, 255)
        text = ["隙間あり(ドット指定)", "隙間あり(角度指定)"][self.mode]
        g.systems.debug_sys.text(f"{text} value={self.value}", WHITE_COLOR)
        g.systems.debug_sys.text("- controls -", WHITE_COLOR)
        g.systems.debug_sys.text("KEY_1 : change mode", WHITE_COLOR)
        g.systems.debug_sys.text(f"KEY_Z, KEY_X : change value", WHITE_COLOR)

if __name__ == '__main__':
    main.main(Scene_TryPie(), window_width=1200)
