# ウィンドウサイズ
DEFAULT_WINDOW_WIDTH  = 640
DEFAULT_WINDOW_HEIGHT = 580

# バトル時、ワールドを描画するスクリーン範囲
DEFAULT_BATTLE_SCREEN_RECT = (0, 0, 640, 480)


#　ゲームの秒間フレーム数
FPS = 60

# ショットの最大速度
MAX_SHOT_VELOCITY = 20

clamp = lambda v, min_value, max_value: min(max_value, max(v, min_value))

# ゲームのシーンID
class SceneId:
    ROOT = "root"
    
    # main game
    MAINGAME                = "maingame"
    MAINGAME_INTRO          = "maingame_intro"
    MAINGAME_READYGO        = "maingame_ready_go"
    MAINGAME_CONTROL_PLAYER = "maingame_control_player"
    MAINGAME_WAIT_LANDING_SHELL = "maingame_wait_landing_shell"
    MAINGAME_TURN_END       = "maingame_turn_end"
    MAINGAME_RESULT         = "maingame_result"
    MAINGAME_PAUSE          = "maingame_pause"
    MAINGAME_EXIT_YESNO     = "maingame_exit_yesno"
    MAINGAME_SKIP_YESNO     = "maingame_skip_yesno"

#------------------------------------------------------------
# 向き
#------------------------------------------------------------
class Dir:
    def is_left(self):
        return self == Dir.LEFT
    
    def is_right(self):
        return self == Dir.RIGHT
    
    # スカラーに変換
    def to_scalar(self):
        if (self.is_left()): return -1
        elif (self.is_right()): return 1
        
        assert False, "謎のDir"
        
        return 0

Dir.LEFT  = Dir()
Dir.RIGHT = Dir()

#------------------------------------------------------------
class ShellType:
    TAKOYAKI = "takoyaki"
    PLASMA   = "plasma"     # 小さな弾
    BIG_TAKO = "big_tako"   # 大きな弾
    WARP     = "warp"       # 移動弾
    
    @classmethod
    def get_types(cls):
        return [cls.TAKOYAKI, cls.PLASMA, cls.BIG_TAKO, cls.WARP]

# 射撃コマンドの定義
SHOT_COMMAND_LIST = {
    'default': [{'time':0.5 }],
    
    ShellType.PLASMA:[
        {'time':0.5 }, {'time':0.55 }, {'time':0.6 }, {'time':0.65 }, {'time':0.7 }
    ]
}

# stage
STAGE_SKY_HEIGHT = 900 # 空の高さ

# idとbitmap indexが同じになるように
class StageId:
    TRAINING = 0
    IWAYAMA  = 1
    MOKUZAI  = 2

    @classmethod
    def id_list(cls):
        return [cls.TRAINING, cls.IWAYAMA, cls.MOKUZAI]

STAGE_DATA_LIST = [
    'stage00.png', 'stage01.png', 'stage02.png'
]

def float_format(f):
    return '{:.3f}'.format(f)

class MouseTargetId:
    MAINGAME    = 0 # メインゲームの描画領域
    UI          = 1 # 画面下の画面
    SKIP_BTN    = 2
    EXIT_BTN    = 3
    INVENTORY   = 4 # プレイヤーのインベントリ
    
    DIALOG_YES  = 5
    DIALOG_NO   = 6

SOUND_DATA_LIST = [
    # bgm
    ("menu",        "Blue_Garnet.mp3"),
    ("stage000",    "Subject_System.mp3"),
    ("stage001",    "Pop_Plus_Steps.mp3"),
    ("stage002",    "Bloom_Bloom.mp3"),
    
    # se
    ("se_explode",  "bom.mp3"),
    ("se_result",   "handclap.mp3"),
    ("se_shoot",    "shoot.mp3"),
    ("se_shoot1",   "shoot17.mp3"),
    ("se_shoot2",   "bom.mp3"),
    ("se_turn",     "turn.mp3"),
    ("se_walk",     "walk.mp3"),
    ("se_warp",     "warp.mp3"),
    ("se_inventory_push_item",  "push30.mp3"),
    ("se_clock",    "clock.mp3")
]

def play_bgm(systems, sound_name):
    snd = systems.res_sys.sound.get_sound(sound_name)
    systems.sound_sys.play_bgm(snd)

def stop_bgm(systems):
    systems.sound_sys.stop_bgm()

def play_se(systems, sound_name):
    snd = systems.res_sys.sound.get_sound(sound_name)
    systems.sound_sys.play_once_se(snd)