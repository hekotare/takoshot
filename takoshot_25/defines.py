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

#------------------------------------------------------------
# ゲームのシーンID
#------------------------------------------------------------
class SceneId:
    ROOT = "root"
    
    # Game_Root
    GAME_ROOT               = "game_root"

    # battle設定画面
    PREPARING_FOR_BATTLE    = "preparing_for_battle"
    
    # main game
    MAINGAME                = "maingame"
    MAINGAME_INTRO          = "maingame_intro"
    MAINGAME_READYGO        = "maingame_ready_go"
    MAINGAME_BEFORE         = "maingame_before"
    MAINGAME_CONTROL_PLAYER = "maingame_control_player"
    MAINGAME_WAIT_LANDING_SHELL = "maingame_wait_landing_shell"
    MAINGAME_TURN_END       = "maingame_turn_end"
    MAINGAME_RESULT         = "maingame_result"
    MAINGAME_PAUSE          = "maingame_pause"
    MAINGAME_EXIT_YESNO     = "maingame_exit_yesno"
    MAINGAME_SKIP_YESNO     = "maingame_skip_yesno"

#------------------------------------------------------------
# キャラクター
#------------------------------------------------------------
class ChrType:
    ORANGE  = "Orange"
    GREEN   = "Green"
    BLUE    = "Blue"
    MAGENTA = "Magenta"
    BROWN   = "Brown"
    INDIGO  = "Indigo"
    BLACK   = "Black"
    WHITE   = "White"

CHARA_DATA_LIST = [
    # type              ビットマップ名
    [ ChrType.ORANGE,   'chr001'],
    [ ChrType.GREEN,    'chr002'],
    [ ChrType.BLUE,     'chr003'],
    [ ChrType.MAGENTA,  'chr004'],
    [ ChrType.BROWN,    'chr005'],
    [ ChrType.INDIGO,   'chr006'],
    [ ChrType.BLACK,    'chr007'],
    [ ChrType.WHITE,    'chr008']
]

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
# 弾
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

# 弾の滞空時間と攻撃力、攻撃範囲のレート
SHOT_RATE_LIST = [
    # sec   damage rate     radius rate
    [6.0,   4.0,            3.0],
    [5.0,   3.5,            2.5],
    [4.0,   3.0,            2.0],
    [3.0,   2.5,            1.75],
    [2.0,   1.5,            1.5],
    [0.0,   1.0,            1.0],
]

SHELL_DEF_LIST = [
    #                       radius damage
    [ShellType.TAKOYAKI,    19,     16],
    [ShellType.PLASMA,      10,      5], # x 4
    [ShellType.BIG_TAKO,    40,      7],
]

#------------------------------------------------------------
# stage
STAGE_SKY_HEIGHT = 900 # 空の高さ

# idとbitmap indexが同じになるように
class StageId:
    TRAINING = 0
    IWAYAMA  = 1
    MOKUZAI  = 2
    GRASS    = 3
    ISLAND   = 4
    TAKOYAKI = 5

STAGE_DATA_LIST = [
    # stage id             stage data      bgm name
    [StageId.TRAINING,    'stage00.png', 'stage000'],
    [StageId.IWAYAMA,     'stage01.png', 'stage001'],
    [StageId.MOKUZAI,     'stage02.png', 'stage000'],
    [StageId.GRASS,       'stage03.png', 'stage001'],
    [StageId.ISLAND,      'stage04.png', 'stage002'],
    [StageId.TAKOYAKI,    'stage05.png', 'stage002'],
]

#------------------------------------------------------------
class MouseTargetId:
    MAINGAME    = 0 # メインゲームの描画領域
    UI          = 1 # 画面下の画面
    SKIP_BTN    = 2
    EXIT_BTN    = 3
    INVENTORY   = 4 # プレイヤーのインベントリ
    RESULT_OK   = 5 # 結果画面のOKボタン
    
    DIALOG_YES  = 6
    DIALOG_NO   = 7
    
    SHOTBAR_TRI_0 = 8
    SHOTBAR_TRI_1 = 9

#------------------------------------------------------------
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
    ("se_clock",    "clock.mp3"),
    ("se_next_phase", "freeze00.mp3")
]

def play_bgm(systems, sound_name):
    snd = systems.res_sys.sound.get_sound(sound_name)
    systems.sound_sys.play_bgm(snd)

def stop_bgm(systems):
    systems.sound_sys.stop_bgm()

def play_se(systems, sound_name):
    snd = systems.res_sys.sound.get_sound(sound_name)
    systems.sound_sys.play_once_se(snd)

#------------------------------------------------------------
def float_format(f):
    return '{:.3f}'.format(f)

class BattleInitInfo:
    
    @classmethod
    def create_1vs1(cls, stage_id = StageId.IWAYAMA):
        info = BattleInitInfo()
        info.stage_id = stage_id
        
        return info
    
    def __init__(self):
        self.player_0 = ChrType.ORANGE
        self.player_1 = ChrType.GREEN
        self.stage_id = StageId.IWAYAMA
