import math

from defines import FPS


class TimeSys:

    def init(self):
        self.sys_frames = 0
        self.sys_time_ms = 0
    
    # 現在のシステム時間（ミリ秒単位）を返す
    def get_sys_time_ms(self):
        return self.sys_time_ms
    
    # 現在のシステムフレーム数を返す
    def get_sys_frames(self):
        return self.sys_frames
    
    # システム時間を１フレームだけ進める
    def step_sys_frame(self):
        self.sys_frames += 1
        self.sys_time_ms = int(self.sys_frames * (1/FPS) * 1000)
