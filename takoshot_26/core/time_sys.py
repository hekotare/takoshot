import math


class TimeSys:
    TYPE_WORLD_TIMER = 1
    TYPE_SYS_TIMER  = 2

    def init(self, fps):
        self.fps = fps
        self.world_frames = 0
        self.world_time_ms = 0
        self.sys_frames = 0
        self.sys_time_ms = 0
    
    # ワールド時間を1フレームだけ進める
    def step_world_frame(self):
        self.world_frames += 1
        self.world_time_ms = int(self.world_frames * (1/self.fps) * 1000)
    
    # システム時間を１フレームだけ進める
    def step_sys_frame(self):
        self.sys_frames += 1
        self.sys_time_ms = int(self.sys_frames * (1/self.fps) * 1000)
    
    def create_world_timer(self):
        return Timer(self, TimeSys.TYPE_WORLD_TIMER)
    
    def create_sys_timer(self):
        return Timer(self, TimeSys.TYPE_SYS_TIMER)
    
    # 一定の時間で-1.0～1.0を繰り返す
    # freq_ms       周期（ミリ秒）
    # offset_ms     タイミングずらす（ミリ秒）
    def cos_wave(self, freq_ms, offset_ms = 0):
        t = self.sys_time_ms + offset_ms
        t = ((t % freq_ms) / freq_ms) # 0.0～1.0
        t = t * math.pi * 2 # 0.0 ～ 2radian

        return math.cos(t)


# 1.終了時間かどうかを調べるために使う
# 2.現在の時間を記録するために使う
class Timer:
    
    def __init__(self, time_sys, time_type):
        self._time_sys          = time_sys
        self._time_type         = time_type
        self._start_time_ms     = -1
        self._duration_time_ms  = -1
    
    # タイマー開始
    def start(self, duration_time_ms):
        self._start_time_ms     = self.get_time_ms()
        self._duration_time_ms  = duration_time_ms
    
    # 開始時間のみ記録、終了時間なし
    def timestamp(self):
        self.start(-1)
    
    def clear(self):
        self._start_time_ms     = -1
        self._duration_time_ms  = -1
    
    def enabled(self):
        return self._start_time_ms != -1
    
    # タイマーの終了時間があるか？
    def has_duration_time(self):
        return self._duration_time_ms != -1
    
    # 開始時間からの経過時間を取得
    @property
    def elapsed_time(self):
    
        if (not self.enabled()): return -1
        
        return (self.get_time_ms() - self._start_time_ms)
    
    # 終了時間までの残り時間を取得
    @property
    def timeleft(self):
    
        # 終了時間がない
        if (not self.has_duration_time()): return -1
        
        return max(0, self._duration_time_ms - self.elapsed_time)
    
    # タイマーの進捗状況（タイマーが開始されているなら0.0～1.0, タイマーが開始されていないなら-1)
    #
    #   (現在時間 - 開始時間) / 持続時間
    @property
    def progress(self):
    
        if (not self.has_duration_time()): return -1
        
        # ゼロ除算回避用
        if (self._duration_time_ms == 0): return 1.0
        
        p = self.elapsed_time / self._duration_time_ms
        
        return min(p, 1.0)
    
    # タイマーが終了したか？
    def is_finished(self):

        time = self.progress
        
        if (time == -1): return False
        
        return 1 <= time
    
    def get_time_ms(self):
        if (self._time_type == TimeSys.TYPE_WORLD_TIMER):
            return self._time_sys.world_time_ms
        else: # TimeSys.TYPE_SYS_TIMER
            return self._time_sys.sys_time_ms