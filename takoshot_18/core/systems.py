import globals as g
from core.input_sys import InputSys
from core.time_sys import TimeSys
from data.bitmap_data import BitmapDataManager


class Systems:
    
    def __init__(self):
        
        self.res_sys = ResourceSys()
        self.res_sys.init()

        self.debug_sys = DebugSys()
        self.debug_sys.init()
        
        self.time_sys = TimeSys()
        self.time_sys.init()
        
        self.input_sys = InputSys()
        self.input_sys.init(self.time_sys)
    
    def begin_process(self):
        self.input_sys.process_key()
        self.debug_sys.clear_text()
    
    def end_process(self):
        self.input_sys.end_process()
        self.time_sys.step_sys_frame()

# ゲームのリソースを追加
class ResourceSys:

    def init(self):
        self.bitmap = BitmapDataManager()
        self.bitmap.load()

class DebugSys:

    def init(self):
        self.x = 700
        self.y = 20
        self.text_param_list = []
    
    def clear_text(self):
        self.text_param_list = []
    
    def text(self, *args, **kwargs):
        kwargs['font'] = g.font_16
        kwargs['background'] = (0, 0, 0)
        self.text_param_list.append([args, kwargs])
    
    def render(self):

        for i, text_param in enumerate(self.text_param_list):
            args, kwargs = text_param
            # テキストカラー指定がなかった場合は、デフォルトで白にする
            if (len(args) == 1): args = (args[0], (255, 255, 255))
            
            g.graphics.text((self.x, self.y + i * 30), *args, **kwargs)