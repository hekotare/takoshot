# ウィンドウサイズ
DEFAULT_WINDOW_WIDTH  = 640
DEFAULT_WINDOW_HEIGHT = 580

# バトル時、ワールドを描画するスクリーン範囲
DEFAULT_BATTLE_SCREEN_RECT = (0, 0, 640, 480)


#　ゲームの秒間フレーム数
FPS = 60

clamp = lambda v, min_value, max_value: min(max_value, max(v, min_value))

# ゲームのシーンID
class SceneId:
    ROOT = "root"
    
    # main game
    MAINGAME                = "maingame"
    MAINGAME_INTRO          = "maingame_intro"
    MAINGAME_READYGO        = "maingame_ready_go"
    MAINGAME_CONTROL_PLAYER = "maingame_control_player"
    MAINGAME_TURN_END       = "maingame_turn_end"
    MAINGAME_RESULT         = "maingame_result"
    MAINGAME_PAUSE          = "maingame_pause"

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