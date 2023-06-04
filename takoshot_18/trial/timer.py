import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene


# タイマー
#
# python -m trial.timer を入力し実行
class Scene_TryTimer(Scene):

    def prepare(self):
        self.pause = False
        self.t0 = g.systems.time_sys.create_world_timer()
        self.t1 = g.systems.time_sys.create_sys_timer()
    
    def update(self):
    
        if (g.systems.input_sys.is_push(KeyCodes.SPACE)):
            self.pause = not self.pause
        
        # ゲームワールドの時間を1つ進める
        if (not self.pause):
            g.systems.time_sys.step_world_frame()
        
        # ゲームタイマーを操作
        if (g.systems.input_sys.is_push(KeyCodes.A)):
            self.t0.start(3000)
        if (g.systems.input_sys.is_push(KeyCodes.S)):
            self.t0.timestamp()
        if (g.systems.input_sys.is_push(KeyCodes.D)):
            self.t0.clear()
        
        # システムタイマーを操作
        if (g.systems.input_sys.is_push(KeyCodes.Z)):
            self.t1.start(3000)
        if (g.systems.input_sys.is_push(KeyCodes.X)):
            self.t1.timestamp()
        if (g.systems.input_sys.is_push(KeyCodes.C)):
            self.t1.clear()
    
    def render(self):
        ms = g.systems.time_sys.world_time_ms
        
        if self.pause:
            g.graphics.text((20, 20), f"ワールド時間 = {ms} (停止中)", (200, 100, 100))
        else:
            g.graphics.text((20, 20), f"ワールド時間 = {ms}", (255, 255, 255))
        
        self.draw_timer(self.t0, "ワールドタイマー",   20, 200)
        self.draw_timer(self.t1, "システムタイマー", 20, 400)
    
    DISABLE_COLOR    = (128,  32,  32)
    ENABLE_BG_COLOR  = ( 32,  32,  32)
    ENABLE_COLOR     = (128, 128, 255)
    
    def draw_timer(self, timer, name, x, y):
    
        g.graphics.text((x, y - 28), name + " [" + self.get_status(timer) + "]", (255, 255, 255))
        
        font = g.font_16
        color = self.ENABLE_BG_COLOR if (timer.enabled()) else self.DISABLE_COLOR
        
        g.graphics.rectangle((x, y, 400, 32), fill=color, outline=(32, 32, 32))
        
        # タイマーの進行度を表示
        if (timer.progress != -1):
            g.graphics.rectangle((x, y, 400 * timer.progress, 32), fill=self.ENABLE_COLOR, outline=(32, 32, 32))
        
        # 終了していたら終了マーク
        if (timer.is_finished()):
            t = g.systems.time_sys.cos_wave(1000)
            g.graphics.rectangle((x, y, 400, 32), outline=(255, 128 + 127 * t, 128 + 127 * t), width = 4)
        
        # タイマーが有効なら開始と終了時間を書く
        if (timer.enabled()):
            g.graphics.text((x + 100, y + 6), f"elapsed_time = {timer.elapsed_time}", (255, 255, 255), background=(0, 0, 0), font=font, textalign="center")
            g.graphics.text((x + 300, y + 6), f"timeleft = {timer.timeleft}", (255, 255, 255), background=(0, 0, 0), font=font, textalign="center")

    def get_status(self, timer):
    
        if (timer.enabled()):
            if (timer.has_duration_time()):
                return "開始"
            else:
                return "永続"
        
        return "無効"


if __name__ == '__main__':
    main.main(Scene_TryTimer())
