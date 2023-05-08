import globals as g
import main
from core.input_sys import KeyCodes, KeyState
from core.scene import Scene


# キー入力システムのテスト
#
# python -m trial.input_sys を入力し実行
class Scene_TryInputSys(Scene):

    key_code_list = [KeyCodes.Z, KeyCodes.X, KeyCodes.C, KeyCodes.MOUSE_LEFT, KeyCodes.MOUSE_RIGHT, KeyCodes.MOUSE_WHEEL]
    key_name_list = ['KEY_Z', 'KEY_X', 'KEY_C', 'MOUSE_LEFT', 'MOUSE_RIGHT', 'MOUSE_WHEEL']
    repeat_list = [30, 60, 120] # キーをリピートするフレーム数（60FPSのゲームでrepeat=60なら、1秒に1回リピートする）

    def prepare(self):
        
        # キー状態のログ
        l = []
        for _ in self.key_code_list:
            key_log = [KeyState.Free] * 30
            l.append(key_log)
        
        self.key_log_list = l
        
        # ボタン押しっぱなし時のキーリピートのログ
        r = []
        for _ in self.repeat_list:
            key_log = [0] * 60
            r.append(key_log)
        
        self.repeat_log_list = r
    
    def update(self):
        input_sys = g.systems.input_sys
        
        # キー状態のログを取る
        for i, key in enumerate(self.key_code_list):
            log_list = self.key_log_list[i]
            log_list.pop(0) # 古いログを削除する
            log_list.append(input_sys.get_key_state(key))
        
        # Zキーを押しっぱなしにしたときのリピートをチェック
        for i, repeat in enumerate(self.repeat_list):
            log_list = self.repeat_log_list[i]
            log_list.pop(0)

            value = 0
            if (input_sys.is_push(KeyCodes.Z)): value = 1
            elif (input_sys.is_hold(KeyCodes.Z, repeat)): value = 2
            
            log_list.append(value)
    
    def render(self):
        
        # キー状態のログを描画
        for i, log_list in enumerate(self.key_log_list):
        
            y = i * 20 + 100
            g.graphics.text((20, y), self.key_name_list[i], (255, 255, 255), font=g.font_i20)
            
            for x, key_state in enumerate(log_list):
                 
                if (key_state == KeyState.Push):    color = (255, 128, 128)
                if (key_state == KeyState.Hold):    color = (128, 255, 128)
                if (key_state == KeyState.Release): color = (128, 128, 255)
                if (key_state == KeyState.Free):    color = (0, 0, 0)
                
                g.graphics.rectangle((x * 20 + 180, y, 20, 20), fill=color, outline=(255, 255, 255), width=1)
        
        # キーのリピートのログを描画
        for i, repeat in enumerate(self.repeat_list):
            y = i * 20 + 300
            g.graphics.text((20, y), f"KEY_Z REPEAT {repeat} FRAME", (255, 255, 255))

            for x, repeat_log in enumerate(self.repeat_log_list[i]):
            
                color = (0, 0, 0)
                if (repeat_log == 1):   color = (255, 128, 128)
                elif (repeat_log == 2): color = (128, 255, 128)

                g.graphics.rectangle((x * 10 + 300, y, 10, 20), fill=color, outline=(255, 255, 255), width=1)

if __name__ == '__main__':
    main.main(Scene_TryInputSys(), window_width=1000)
