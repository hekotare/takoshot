import pygame

import globals as g
import graphics as gra
from core.scene import Scene_Container

gra_window = None

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