import globals as g
from core.input_sys import InputSys
from core.sound_sys import SoundSys
from core.time_sys import TimeSys
from data.bitmap_data import BitmapDataManager
from data.character_data import ChrDataManager
from data.sound_data import SoundDataManager
from data.stage_data import StageDataManager


class Systems:
    
    def __init__(self):
        
        self.res_sys = ResourceSys()
        self.res_sys.init()

        self.debug_sys = DebugSys()
        self.debug_sys.init()

        self.sound_sys = SoundSys()
        self.sound_sys.init()

        self.time_sys = TimeSys()
        self.time_sys.init()
        
        self.input_sys = InputSys()
        self.input_sys.init(self.time_sys)

        self.mouse_target_sys = MouseTargetSys()
        self.mouse_target_sys.init()
    
    def begin_process(self):
        self.input_sys.process_key()
        self.debug_sys.clear_text()
        self.mouse_target_sys.hittest_mouse_target()
    
    def end_process(self):
        self.input_sys.end_process()
        self.time_sys.step_sys_frame()

# マウスターゲットを調べる
class MouseTargetSys:

    ModalDialog = {}
    
    def init(self):
        self.target_list = []
    
    def hittest_mouse_target(self):
    
        mx, my = g.systems.input_sys.mouse_pos
        
        self.current_target_id = -1
        self.current_target_rect = None
        
        # 優先度の高いエリアから順に判定
        for target in reversed(self.target_list):
        
            # モーダルダイアログならそれ以下の優先度の低い判定をやめる
            if (target == self.ModalDialog):
                break
            
            x, y, w, h, id = *target[0], target[1]
            
            if (x <= mx <= x + w and y <= my <= y + h):
                self.current_target_rect = (x, y, w, h)
                self.current_target_id = id
                break
        
        # 判定が終わったので消す
        self.target_list = []
    
    def add_mouse_target(self, area_rect, id):
        self.target_list.append((area_rect, id))
    
    def has_mouse_target(self):
        return self.current_target_id != -1
    
    # モーダルダイアログ作成用に追加
    def add_modal_dialog(self):
        self.target_list.append(self.ModalDialog)


# ゲームのリソースを追加
class ResourceSys:

    def init(self):
        self.bitmap = BitmapDataManager()
        self.bitmap.load()

        self.sound = SoundDataManager()
        self.sound.load()

        self.chrdata = ChrDataManager()
        self.chrdata.load()

        self.stage = StageDataManager()
        self.stage.load(self.bitmap)

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
    
        if (g.DebugFlags.DISPLAY_CURRENT_MOUSE_TARGET and g.systems.mouse_target_sys.has_mouse_target()):
            t = g.systems.time_sys.cos_wave(2000) # 0～1
            g.graphics.rectangle(g.systems.mouse_target_sys.current_target_rect, outline=(128 + 127 * t, 128, 128), width = 4)
            self.text(f"mouse_target_id={g.systems.mouse_target_sys.current_target_id}")
        
        for i, text_param in enumerate(self.text_param_list):
            args, kwargs = text_param
            # テキストカラー指定がなかった場合は、デフォルトで白にする
            if (len(args) == 1): args = (args[0], (255, 255, 255))
            
            g.graphics.text((self.x, self.y + i * 30), *args, **kwargs)