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
    
    # 一定の時間で-1.0～1.0を繰り返す
    # freq_ms       周期（ミリ秒）
    # offset_ms     タイミングずらす（ミリ秒）
    def cos_wave(self, freq_ms, offset_ms = 0):
        t = self.get_sys_time_ms() + offset_ms
        t = ((t % freq_ms) / freq_ms) # 0.0～1.0
        t = t * math.pi * 2 # 0.0 ～ 2radian

        return math.cos(t)
