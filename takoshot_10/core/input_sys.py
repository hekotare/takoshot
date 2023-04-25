import enum

import pygame
from pynput import keyboard


class KeyState:
    Push    = 0x01 # 押した瞬間
    Hold    = 0x02 # 押され続けている
    Release = 0x04 # 離した瞬間
    Free    = 0x08 # 押されていない

class InputSys:

    def __init__(self):
        self._keyboard_listener = None
        self._keystate_list = [KeyState.Free] * KeyCodes.KEY_NUM
        self._pressed_list = [False] * KeyCodes.KEY_NUM
        self._time_list = [0] * KeyCodes.KEY_NUM # キーを押したときの時間（フレーム）を記録しておく（キーのリピートに使う）
        self._observe_list = [] # 現在押されているキー（監視対象とする）
        self.mouse_pos = (0, 0)
        self.mouse_move = (0, 0)
        self.delta = 0
    
    def init(self, time_sys):
        self._time_sys = time_sys # キーのリピート押しのために追加
        self._keyboard_listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self._keyboard_listener.start()
    
    def is_push(self, vk):
        return self.is_key_state(vk, KeyState.Push)
    
    # repeat_frame ボタンを一定間隔でリピート押しする場合に使う
    def is_hold(self, vk, repeat_frame = 0):
        return self._is_repeat(vk, repeat_frame) and self.is_key_state(vk, KeyState.Hold)
    
    def _is_repeat(self, vk, repeat_frame = 0):
    
        if (repeat_frame <= 0): return True # リピート設定なし
        
        elapsed_frame = self._time_sys.get_sys_frames() - self._time_list[vk]
        
        n = elapsed_frame % repeat_frame
        
        return repeat_frame <= elapsed_frame and n == 0
    
    def is_release(self, vk):
        return self.is_key_state(vk, KeyState.Release)
    
    def is_free(self, vk):
        return self.is_key_state(vk, KeyState.Free)
    
    def is_keydown(self, vk, repeat_frame = 0):
        return self.is_push(vk) or self.is_hold(vk, repeat_frame)
    
    def is_keyup(self, vk):
        return self.is_key_state(vk, KeyState.Release | KeyState.Free)
    
    def is_key_state(self, vk, key_state):
        return (self._keystate_list[vk] & key_state) != 0
    
    def get_key_state(self, vk):
        return self._keystate_list[vk]
    
    # 毎フレームの開始時に呼び出す
    def process_key(self):
    
        for vk in self._observe_list[:]:
            new_key_state = self._update_key_state(vk, self._pressed_list[vk], self._keystate_list[vk])
            if (new_key_state == KeyState.Free):
                self._observe_list.remove(vk) # キー状態がフリーになったので、監視対象から外す
        
        # とりあえずの処理でマウスも追加
        mouse_pressed = pygame.mouse.get_pressed()
        self._update_key_state(KeyCodes.MOUSE_LEFT,  mouse_pressed[0], self._keystate_list[KeyCodes.MOUSE_LEFT])
        self._update_key_state(KeyCodes.MOUSE_WHEEL, mouse_pressed[1], self._keystate_list[KeyCodes.MOUSE_WHEEL])
        self._update_key_state(KeyCodes.MOUSE_RIGHT, mouse_pressed[2], self._keystate_list[KeyCodes.MOUSE_RIGHT])
        
        old_mouse_pos = self.mouse_pos
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_move = self.mouse_pos[0] - old_mouse_pos[0], self.mouse_pos[1] - old_mouse_pos[1]
    
    def end_process(self):
        self.delta = 0

    # とりあえずこんなんでいい？
    # 
    # マウスホイールのスクロール量を調べる方法がよくわからなかったので、
    # 外部でマウスイベントをチェックし、スクロール量をセットするようにした
    def on_mousewheel_delta(self, delta):
        self.delta += delta
    
    def _update_key_state(self, vk, pressed, old_key_state):
    
        if pressed:
            if (old_key_state & (KeyState.Free | KeyState.Release)) != 0:
                new_key_state = KeyState.Push
            else:
                new_key_state = KeyState.Hold # ボタンを押し続けている
        else:
            if (old_key_state & (KeyState.Push | KeyState.Hold)) != 0:
                new_key_state = KeyState.Release
            else:
                new_key_state = KeyState.Free
        
        self._keystate_list[vk] = new_key_state
        
        return new_key_state
    
    def _on_press(self, key):
        vk = self._key_to_vk(key)
        #print(f'on_press vk={vk}')
        
        if (self._pressed_list[vk] == False):
            self._pressed_list[vk] = True
            
            self._time_list[vk] = self._time_sys.get_sys_frames()
            
            # 観察リストに登録、不要かもしれんけど一応重複チェック
            if vk not in self._observe_list:
                self._observe_list.append(vk)

    def _on_release(self, key):
        vk = self._key_to_vk(key)
        #print(f'on_release vk={vk}')
        
        if (self._pressed_list[vk] == True):
            self._pressed_list[vk] = False
    
    #
    # キー入力イベントからキーの値を得る
    #
    # 特殊キー（shift、スペース、escキーなど）を押したときはEnum型が渡される
    # pynputの_event_to_keyあたりが原因とおもうけどこれは正常な動作？バグ？
    #
    # enum型のときは、enum.value.vkの値を得るようにする
    def _key_to_vk(self, key):
        if isinstance(key, enum.Enum):
            return key.value.vk
        else:
            return key.vk
    

# キーコードの定義（これでいいんかな？）
class KeyCodes:
    BACKSPACE = 8
    TAB = 9
    ENTER = 13
                    
    #SHIFT = 16
    LSHIFT = 160
    RSHIFT = 161
    
    CTRL = 17
    PAUSE = 19
    CAPSLOCK = 20
    ESC = 27
    SPACE = 32
                    
    PAGEUP = 33
    PAGEDOWN = 34
    END = 35
    HOME = 36
                    
    LEFT = 37
    UP = 38
    RIGHT = 39
    DOWN = 40
                    
    INSERT = 45
    DELETE = 46
                    
    KEY_0 = 48
    KEY_1 = 49
    KEY_2 = 50
    KEY_3 = 51
    KEY_4 = 52
    KEY_5 = 53
    KEY_6 = 54
    KEY_7 = 55
    KEY_8 = 56
    KEY_9 = 57
                    
    A = 65
    B = 66
    C = 67
    D = 68
    E = 69
    F = 70
    G = 71
    H = 72
    I = 73
    J = 74
    K = 75
    L = 76
    M = 77
    N = 78
    O = 79
    P = 80
    Q = 81
    R = 82
    S = 83
    T = 84
    U = 85
    V = 86
    W = 87
    X = 88
    Y = 89
    Z = 90
    
    NUMPAD0 = 96
    NUMPAD1 = 97
    NUMPAD2 = 98
    NUMPAD3 = 99
    NUMPAD4 = 100
    NUMPAD5 = 101
    NUMPAD6 = 102
    NUMPAD7 = 103
    NUMPAD8 = 104
    NUMPAD9 = 105
    MULTIPLY = 106
    ADD = 107
                    
    SUBTRACT = 109
    DECIMAL = 110
    DIVIDE = 111
                    
    F1 = 112
    F2 = 113
    F3 = 114
    F4 = 115
    F5 = 116
    F6 = 117
    F7 = 118
    F8 = 119
    F9 = 120
    F10 = 121
    F11 = 122
    F12 = 123
                    
    NUMLOCK = 144
    SCROLL_LOCK = 145
    
    COLON = 186
    PLUS = 187 # ;+
    COMMA = 188 # ,<
    MINUS = 189 # -=
    PERIOD = 190 # .>
    QUESTION = 191 # ?
    OPEN_BRACKET = 219
    CLOSED_BRACKET = 221
    UNDER_SCORE = 226

    MOUSE_LEFT = 256
    MOUSE_WHEEL = 257
    MOUSE_RIGHT = 258
                    
    KEY_NUM = 260
