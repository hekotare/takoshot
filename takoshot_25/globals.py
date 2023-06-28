surface = None
graphics = None

class DebugFlags:
    DISPLAY_CURRENT_MOUSE_TARGET = True # マウスターゲットの枠を表示
    DISPLAY_PLAYER_POSTURE = False # プレイヤーの姿勢を描画
    DISPLAY_SCENE_ID = True # シーンのIDを表示
    DISPLAY_PLAYER_SIGHT_BORDER = False
    DISPLAY_PLAYER_MUZZLE_POSITION = True
    CHECK_calc_viewarea_in_world2 = False
    PRINT_calc_viewarea_in_world2 = False
    PRINT_update_waypoint = False


# フォント
default_font = None
font_8 = None
font_10 = None
font_16 = None
font_20 = None
font_40 = None
font_i20 = None
font_i40 = None
font_i80 = None