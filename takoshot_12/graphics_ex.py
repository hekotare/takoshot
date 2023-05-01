import pygame

import globals as g
import graphics as gra
from core.scene import Scene_Container

SIGHT_RADIUS = 100
gra_window  = None
gra_sight   = None

def draw_stage(stage):
    g.graphics.blit(stage.surf, (0, 0))


def draw_player(player):

    # ビットマップのインデックス
    idx = 0
    
    foot_idx = int(player.foot_step / 6) % 4
    
    if (foot_idx == 1):
        idx = 1
    elif (foot_idx == 3):
        idx = 2
    
    if (player.dir.is_left()):
        idx += 9
    
    surf = g.systems.res_sys.bitmap.get_bitmap("chr001", idx)
    
    g.graphics.rotate_blit(surf, (player.x, player.y),
        (surf.get_width() * 0.5, surf.get_height() * 0.75), player.posture_to_rotate_degree())

    # debug posture
    if (g.DebugFlags.DISPLAY_PLAYER_POSTURE):
        g.graphics.text((player.x, player.y + 30), f"posture_deg={int(player.posture_degree)}", (255, 255, 255), background=(0, 0, 0), font=g.font_16)
        g.graphics.text((player.x, player.y + 50), f"rotate_deg={int(player.posture_to_rotate_degree())}", (255, 255, 255), background=(0, 0, 0), font=g.font_16)


# プレイヤー射撃時の照準を描画
# 
# scale 0.0～1.0
def draw_player_sight(player, scale):

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
    
    surf = gra_sight.target
    x, y = player.get_muzzle_position()
    g.graphics.blit(surf, (x - surf.get_width() * 0.5, y - surf.get_height() * 0.5))

    '''
        画面にgra_sightを描画する
    '''
    #blit_w(transform, gra_sight.target, *player.get_muzzle_position(), 0.0, 1.0, 0.5, 0.5)


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

def draw_player_muzzle_position(surface, player):
    x, y = player.get_muzzle_position()
    draw_point_and_label(surface, x, y, "muzzle_point")

def draw_point_and_label(surface, x, y, label):
    color = (192, 0, 32)
    
    gra.circle(surface, (x, y), 3, fill=color)
    gra.line(surface, color, (x, y), (x - 20, y - 20))
    w, h = g.font_8.size(label)
    gra.text(surface, (x - 20 - w * 0.5, y - 20 - h), label, color, font=g.font_8)

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

# シーンのidを階層的に描画する
def draw_scene_id(scene, depth = 0):

    color = UI_SCENE_UPDATED if scene.last_update_time_ms == g.systems.time_sys.sys_time_ms else UI_SCENE_NO_UPDATE
    g.systems.debug_sys.text(" " * (depth * 2) + f"{scene.id}", color)
    
    if (isinstance(scene, Scene_Container)):
        for child in scene.children:
            draw_scene_id(child, depth + 1)