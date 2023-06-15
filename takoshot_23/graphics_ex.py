import math

import pygame

import globals as g
import graphics as gra
from core.scene import Scene_Container
from defines import FPS, MouseTargetId, ShellType, play_se
from geometry import Geometry

SIGHT_RADIUS = 100
UI_PLAYER_BAR_WIDTH  = 80
UI_PLAYER_BAR_HEIGHT = 5

particle_circle_surface = None
gra_window  = None
gra_sight   = None
graphics_hud = None

# x, y, rotate_deg, scale       ワールド座標系の値
# img_center_x, img_center_y    画像の中心座標（0.0～1.0）
def blit_w(transform, img, x, y, rotate_deg, scale, img_origin_x, img_origin_y, special_flags = 0):
    x, y, r, s = transform.world_to_screen(x, y, rotate_deg, scale)
    g.graphics.blit3(img, (x, y), s, r, (img_origin_x, img_origin_y), special_flags = special_flags, clip_rect = g.BATTLE_SCREEN_RECT)

def draw_stage(stage, transform):
    blit_w(transform, stage.surf, *stage.offset, 0, 1.0, 0, 0)

def draw_player(player, transform):

    # ビットマップのインデックス
    idx = -1
    
    if player.is_alive():
        if player.is_shooting():
            p = player.shot_timer.progress
            if p < 0.5: idx = 6
            elif p < 0.75: idx = 7
            else: idx = 8
        else:
            # 歩き
            foot_idx = int(player.foot_step / 6) % 4
            
            if (foot_idx == 1):
                idx = 1
            elif (foot_idx == 3):
                idx = 2
            else:
                idx = 0
            
            # play se
            if player.ex_prop['old_foot_idx'] != idx:
                player.ex_prop['old_foot_idx'] = idx
                play_se(g.systems, "se_walk")

    elif player.is_destoryed():
        idx = 3 # やられた
    
    if idx == -1: return # LOST状態
    
    # 反転処理
    if (player.dir.is_left()):
        idx += 9
    
    surf = g.systems.res_sys.bitmap.get_bitmap("chr001", idx)
    
    blit_w(transform, surf, player.x, player.y, player.posture_to_rotate_degree(), 1.0, 0.5, 0.75)
    
    # debug posture
    if (g.DebugFlags.DISPLAY_PLAYER_POSTURE):
        x, y = transform.world_to_screen_xy(player.x, player.y)
        g.graphics.text((x - 60, y + 30), f"posture_deg={int(player.posture_degree)}", (255, 255, 255), background=(0, 0, 0), font=g.font_16)
        g.graphics.text((x - 60, y + 50), f"rotate_deg={int(player.posture_to_rotate_degree())}", (255, 255, 255), background=(0, 0, 0), font=g.font_16)

def draw_player_status(player, transform):

    global graphics_hud
    
    if (graphics_hud is None):
        graphics_hud = gra.Graphics(pygame.Surface((UI_PLAYER_BAR_WIDTH + 10, 60), pygame.SRCALPHA))
    
    draw_status(player, transform, graphics_hud, UI_PLAYER_BAR_WIDTH, UI_PLAYER_BAR_HEIGHT)

def draw_status(player, transform, gra_hud, bar_width, bar_height):
    gra_hud.fill(0)
    
    # HPバー
    yy = 0
    gra_hud.rectangle((1, 1, bar_width, bar_height), fill=(20, 20, 20), outline=(20, 20, 20))
    gra_hud.rectangle((0, 0, bar_width * (player.hp / player.hp_max), bar_height), fill=(255, 128, 128))
    
    # 移動エネルギーのバー
    yy += bar_height + 1
    gra_hud.rectangle((1, yy + 1, bar_width, bar_height), fill=(20, 20, 20), outline=(20, 20, 20))
    gra_hud.rectangle((0, yy, bar_width * (player.move_energy / player.move_energy_max), bar_height), fill=(128, 128, 255))
    
    yy += bar_height + 4
    # player name
    gra_hud.text((0, yy), player.player_name, (255, 255, 255), font=g.font_20, shadow_color=(0, 0, 0))
    
    if (g.BATTLE_SCREEN_RECT.bottom - player.y <= 100): yy = -100
    
    surf = gra_hud.target
    blit_w(transform, surf, player.x, player.y + yy, 0.0, 1.0, 0.5, 0.0)

def draw_shell(shell, transform):

    frame = g.systems.time_sys.world_time_ms
    bmpname = ""
    bmpidx = 0
    rotate_deg = 0
    
    if (shell.type == ShellType.TAKOYAKI):
        bmpname = 'shell001'
        bmpidx = int(frame / 500 * 6) % 6
    elif (shell.type == ShellType.PLASMA):
        bmpname = 'shell002'
        bmpidx = int(frame / 200) % 3
    elif (shell.type == ShellType.BIG_TAKO):
        bmpname = 'shell003'
    elif (shell.type == ShellType.WARP):
        bmpname = 'shell_warp'
        bmpidx = int(frame / 200) % 2
        
        if shell.velocity != (0, 0):
            rotate_deg = Geometry.vector_to_angle(*shell.velocity)
    
    surf = g.systems.res_sys.bitmap.get_bitmap(bmpname, bmpidx)
    blit_w(transform, surf, shell.x, shell.y, rotate_deg, 1.0, 0.5, 0.5)

def draw_particle(surface, transform, particle):
    draw_circle(surface, transform, particle.x, particle.y, 3.0, particle.color)

def draw_circle(surface, transform, x, y, radius, color):
    xx, yy, r, s = transform.world_to_screen(x, y, 0, radius)
    gra.circle(surface, (xx, yy), max(1, s), fill=color)

def draw_particle2(transform, particle):

    global particle_circle_surface 
    
    if (particle_circle_surface is None):
        particle_circle_surface = pygame.Surface((20, 20), pygame.SRCALPHA) # 十分な大きさを確保
    
    # 透過するためにいったんparticle_circle_surfaceに円を描き込む
    gra.fill(particle_circle_surface, (0, 0, 0, 0))
    gra.circle(particle_circle_surface, (10, 10), particle.radius, fill=(255, 255, 255))
    particle_circle_surface.set_alpha(particle.alpha * 255) # 透過設定
    
    blit_w(transform, particle_circle_surface, particle.x, particle.y, 0, 1.0, 0.5, 0.5)

# プレイヤー射撃時の照準を描画
# 
# scale 0.0～1.0
def draw_player_sight(player, scale, transform):

    if (scale <= 0.0): return
    
    '''
        gra_sightに照準を描画する
    '''
    global gra_sight
    
    radius = SIGHT_RADIUS * scale
    
    if (gra_sight is None):
        width = height = SIGHT_RADIUS * 2 + 8 # 照準が描き込めるように少し大きめに作る
        gra_sight = gra.Graphics(pygame.Surface((width, height), pygame.SRCALPHA)) # 少し大きめに作る
        gra_sight.target.set_alpha(128)
    
    color_list = [(228, 248, 180), (162, 216, 40), (40, 216, 92), (255, 255, 255)]
    
    dir = 1 if player.dir.is_right() else -1 # キャラの向きで反転させる
    
    target_deg = player.shooting_angle * dir
    min_deg = player.shooting_angle_min * dir
    max_deg = player.shooting_angle_max * dir
    rotate_deg = player.posture_to_rotate_degree()
    
    gra_sight.fill(0)
    rect = gra_sight.target.get_rect()
    draw_sight(gra_sight.target, rect.width * 0.5, rect.height * 0.5, radius, target_deg, min_deg, max_deg, rotate_deg, color_list)
    
    if (g.DebugFlags.DISPLAY_PLAYER_SIGHT_BORDER):
        gra_sight.rectangle(rect, outline=(20, 20, 20))
    
    blit_w(transform, gra_sight.target, *player.get_muzzle_position(), 0.0, 1.0, 0.5, 0.5)


# 照準の描画
#
# x, y          中心座標
# radius        照準の半径
# target        照準の角度
# min, max      射撃可能な範囲
# rotate_deg    プレイヤーの回転（照準と射撃範囲を回転させる）
# color_list    照準の色（4色）
def draw_sight(surface, x, y, radius, target_degree, min_degree, max_degree, rotate_deg, color_list):

    color_0 = color_list[0]
    color_1 = color_list[1]
    color_2 = color_list[2]
    color_3 = color_list[3]
    
    # 照準をプレイヤーの姿勢分だけ回転させる
    target_degree -= rotate_deg
    min_degree -= rotate_deg
    max_degree -= rotate_deg
    
    # 外枠
    for i in range(8):
        s = int(i/8 * 360)
        e = int((i + 1)/8 * 360)
        gra.ring(surface, x, y, radius - 4, radius - 8, s, e, 20, fill=color_0, outline=color_0, width=0, space_dot = 8)
    
    # 内枠
    for i in range(16):
        s = int(i/16 * 360)
        e = int((i + 1)/16 * 360)
        gra.ring(surface, x, y, radius - 14, radius - 18, s, e, 20, fill=color_1, outline=color_1, width=0, space_dot = 8)
    
    # 射撃可能な範囲
    gra.pie(surface, x, y, radius - 24, min_degree, max_degree, 20, fill=color_2, outline=color_2, width=0)
    
    # 照準
    gra.pie(surface, x, y, radius, target_degree-2, target_degree+2, 4, fill=color_3)
    gra.ring(surface, x, y, radius + 10, radius, target_degree-2, target_degree+2, 4, fill=color_3)

    # 角度を表示
    v = pygame.Vector2(0, -radius*0.9).rotate(target_degree)
    v.x += x
    v.y += y
    r = int(target_degree%360)
    gra.text(surface, v, str(r), (192, 64, 64), font=g.font_16, textalign='center', valign='middle')

def draw_player_muzzle_position(surface, player, transform):
    x, y = transform.world_to_screen_xy(*player.get_muzzle_position())
    draw_point_and_label(surface, x, y, "muzzle_point")

def draw_point_and_label(surface, x, y, label):
    color = (192, 0, 32)
    
    gra.circle(surface, (x, y), 3, fill=color)
    gra.line(surface, color, (x, y), (x - 20, y - 20))
    w, h = g.font_8.size(label)
    gra.text(surface, (x - 20 - w * 0.5, y - 20 - h), label, color, font=g.font_8)

#------------------------------------------------------------
# UI
#------------------------------------------------------------
def draw_window(rect, color):
    x, y, width, height = rect
    
    global gra_window
    
    if (gra_window is None):
        gra_window = gra.Graphics(pygame.Surface((640, 480), pygame.SRCALPHA))
        gra_window.target.set_alpha(192)
    
    gra_window.fill(0)
    gra_window.rectangle((0, 0, width, height), fill=color)
    
    g.graphics.blit(gra_window.target, (x, y))

UI_SCENE_UPDATED   = (128, 255, 128)
UI_SCENE_NO_UPDATE = (255, 255, 255)

UI_BAR_BORDER       = (255, 255, 255)
UI_BAR_BG           = (32, 32, 32)
UI_BAR_SCALE        = (96, 96, 96)

# プレイヤーのインベントリの中身を描画
def draw_inventory(pos, extent, inventory):

    x, y = pos
    
    n = g.systems.time_sys.cos_wave(2000)
    n = (n + 5.0) / 6 # 0.666.. <= n <= 1.0
    
    for i, item_idx in enumerate(inventory.get_item_index_list()):
        
        if (i == inventory.selected_index):
            c = (192 * n, 255 * n, 128 * n)
        else:
            c = (214, 214, 214)
        
        src_img = g.systems.res_sys.bitmap.get_bitmap('item_icon', item_idx)
        g.graphics.rectangle((x, y, extent, extent), fill=c, outline=(32,32,32), width=1)
        g.graphics.blit(src_img, (x + 4, y + 4))
        
        x += extent
    
    g.systems.mouse_target_sys.add_mouse_target((*pos, extent * len(inventory.get_item_index_list()), extent), MouseTargetId.INVENTORY)

#shot_power_rate    0.0～1.0 
#tri0_pos           0.0～1.0
#tri1_pos           0.0～1.0
def draw_shotbar(rect, shot_power_rate, tri0_pos, tri1_pos, old_power_rate = -1):

    inner_rect = (rect.left + 4, rect.top + 4, rect.width - 8, rect.height - 7)
    
    # 背景
    g.graphics.rectangle(rect, fill = UI_BAR_BORDER, outline = UI_BAR_BG, width = 2)
    g.graphics.rectangle(inner_rect, fill = UI_BAR_BG)
    
    power_rect = pygame.Rect(rect.left + 4, rect.top + 4, rect.width - 8, rect.height - 8)
    
    # 以前のショットパワー
    if (old_power_rate != -1):
        old_power_rect = power_rect.copy()
        old_power_rect.width *= old_power_rate
        g.graphics.rectangle(old_power_rect, fill = (128, 32, 32))
    
    # メモリ
    for i in range(1, 7):
        x = rect[0] + i / 7 * rect[2]
        g.graphics.line(UI_BAR_SCALE, start_pos = (x, rect[1] + 4), end_pos = (x, rect[1] + rect[3] - 4), width = 2)

    # ショットパワー
    power_rect.width *= shot_power_rate
    g.graphics.rectangle(power_rect, fill = (255, 128, 128))
    
    # 三角形
    y0, y1 = rect.top, rect.bottom
    
    x = rect.left + tri0_pos * rect.width
    g.graphics.polygon([[x - 6, y0 - 6], [x + 6, y0 - 6], [x, y0 + 10]], fill=(255, 128,  64), outline=(255, 255, 255), width=2)
    
    x = rect.left + tri1_pos * rect.width
    g.graphics.polygon([[x - 6, y1 + 6], [x + 6, y1 + 6], [x, y1 - 10]], fill=( 64, 128, 255), outline=(255, 255, 255), width=2)

# プレイヤー操作中の残り時間を画面に表示
def draw_timeleft(timeleft):
    # 残り時間を描画
    sec = timeleft * 0.001
    sec = str(int(sec))
    y = g.BATTLE_SCREEN_RECT.top + 40
    
    g.graphics.text((g.BATTLE_SCREEN_RECT.centerx, y), sec, (255, 255, 255), font=g.font_i80, textalign='center', shadow_color=(0, 0, 0))

def draw_battle_background():
    g.graphics.rectangle(g.BATTLE_SCREEN_RECT, fill=(200, 200, 255))
    g.systems.mouse_target_sys.add_mouse_target(g.BATTLE_SCREEN_RECT, MouseTargetId.MAINGAME)

def draw_ui_background():
    g.graphics.rectangle((0, 480, 640, 400), fill=(162, 192, 142), outline=(20, 20, 20), width=2)
    g.systems.mouse_target_sys.add_mouse_target((0, 480, 640, 400), MouseTargetId.UI)

# ボタンの描画とマウスターゲットの登録
def draw_button(x, y, w, h, label, mouse_target_id):

    # マウスカーソルがオーバーライド
    if (g.systems.mouse_target_sys.current_target_id == mouse_target_id):
        btn_color = ( 60, 192, 255)
        str_color = (255, 255, 255)
    else:
        btn_color = (255, 255, 255)
        str_color = (  0,   0,   0)
    
    g.graphics.rectangle((x, y, w, h), fill = btn_color)
    g.graphics.text((x + w * 0.5, y + h * 0.12), label, str_color, font=g.font_i20, textalign="center")

    g.systems.mouse_target_sys.add_mouse_target((x, y, w, h), mouse_target_id)

# シーンのidを階層的に描画する
def draw_scene_id(scene, depth = 0):

    color = UI_SCENE_UPDATED if scene.last_update_time_ms == g.systems.time_sys.sys_time_ms else UI_SCENE_NO_UPDATE
    g.systems.debug_sys.text(" " * (depth * 2) + f"{scene.id}", color)
    
    if (isinstance(scene, Scene_Container)):
        for child in scene.children:
            draw_scene_id(child, depth + 1)