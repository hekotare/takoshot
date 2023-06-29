from core.input_sys import InputSys, KeyCodes
from core.sound_sys import SoundSys
from core.time_sys import TimeSys


class Systems:
    
    def __init__(self, res_sys, FPS):
        
        self.res_sys = res_sys
        self.res_sys.init()

        self.debug_sys = DebugSys()
        self.debug_sys.init(self)

        self.sound_sys = SoundSys()
        self.sound_sys.init()

        self.time_sys = TimeSys()
        self.time_sys.init(FPS)
        
        self.input_sys = InputSys()
        self.input_sys.init(self.time_sys)

        self.mouse_target_sys = MouseTargetSys()
        self.mouse_target_sys.init(self)
    
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
    
    def init(self, systems):
        self.systems = systems
        self.target_list = []
        self.draggable_target_map = {}
        self.dragging_id = None
    
    def hittest_mouse_target(self):
    
        input_sys = self.systems.input_sys
        mx, my = input_sys.mouse_pos
        
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
        
        # ドラッグの開始判定
        if (input_sys.is_push(KeyCodes.MOUSE_LEFT) and
            self.draggable_target_map.get(self.current_target_id) is not None):
            # start drag
            self.dragging_id = self.current_target_id
        
        # ドラッグ中の処理
        if self.dragging_id is not None:
            event_listener = self.draggable_target_map[self.dragging_id]

            # ドラッグオブジェクトが存在しない or マウスボタンが離された
            if (event_listener is None or input_sys.is_keyup(KeyCodes.MOUSE_LEFT)):
                # end drag
                self.dragging_id = None
            else:
                event_listener(mx, my)
        
        # 判定が終わったので消す
        self.target_list = []
        self.draggable_target_map = {}
    
    def add_mouse_target(self, area_rect, id):
        self.target_list.append((area_rect, id))
    
    def has_mouse_target(self):
        return self.current_target_id != -1
    
    # モーダルダイアログ作成用に追加
    def add_modal_dialog(self):
        self.target_list.append(self.ModalDialog)

    def add_draggable_target(self, area_rect, id, event_listener):
        self.target_list.append((area_rect, id))
        self.draggable_target_map[id] = event_listener


class DebugSys:

    def init(self, systems):
        self.systems = systems
        self.x = 700
        self.y = 20
        self.text_param_list = []
    
    def clear_text(self):
        self.text_param_list = []
    
    def text(self, *args, **kwargs):
        self.text_param_list.append([args, kwargs])