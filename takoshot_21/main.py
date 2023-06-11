import sys

import pygame

import globals as g
import graphics
import graphics_ex as gra_ex
from core.scene import Scene_Container
from core.systems import Systems
from defines import *

surface = None

def main(scene, window_width=None, window_height=None):

    systems_init(window_width=window_width, window_height=window_height)

    root = Scene_Container(SceneId.ROOT)
    root.add_child(scene)

    clock = pygame.time.Clock()

    while(True):
        
        g.systems.begin_process()
        
        surface.fill((0, 0, 0))
        g.graphics.fill((0, 0, 0))

        # シーンの更新
        root.update()
        root.render()
        
        # シーン名を描画（とりあえずここに追加）
        if (g.DebugFlags.DISPLAY_SCENE_ID):
            gra_ex.draw_scene_id(root)
        
        g.systems.debug_sys.render()
        
        # fpsの描画
        g.graphics.text((g.WINDOW_RECT.right - 60, 0),
                        str(round(clock.get_fps(), 2)), (255, 255, 255), background=(0, 0, 0))
        
        surface.blit(g.surface, (0, 0))
        
        pygame.display.update()
        
        g.systems.end_process()
        
        clock.tick(FPS)
        
        # event
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # とりあえずこれでいい？
            if event.type == pygame.MOUSEWHEEL:
                g.systems.input_sys.on_mousewheel_delta(event.y) # ホイールの移動量

# システムの初期化
def systems_init(flags=0, window_width=None, window_height=None):

    global surface

    pygame.init()
    
    g.BATTLE_SCREEN_RECT = pygame.Rect(DEFAULT_BATTLE_SCREEN_RECT)

    window_width = window_width or DEFAULT_WINDOW_WIDTH
    window_height = window_height or DEFAULT_WINDOW_HEIGHT
    g.WINDOW_RECT = pygame.Rect(0, 0, window_width, window_height)

    surface = pygame.display.set_mode(
        (g.WINDOW_RECT.width, g.WINDOW_RECT.height), flags)
    pygame.display.set_caption('- takoshot -')
    pygame.mixer.init(frequency=44100)
    
    screen_surface = pygame.Surface(
        (surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    g.surface = screen_surface
    g.graphics = graphics.Graphics(screen_surface)

    # fontの初期化
    g.default_font = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 20)
    g.font_8  = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 8)
    g.font_10 = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 10)
    g.font_16 = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 16)
    g.font_20 = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 20)
    g.font_40 = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 40)
    g.font_i20 = pygame.font.Font("C:\Windows\Fonts\\ariblk.ttf", 16)
    g.font_i40 = pygame.font.Font("C:\Windows\Fonts\\ariblk.ttf", 40)
    g.font_i80 = pygame.font.Font("C:\Windows\Fonts\\ariblk.ttf", 80)
    
    # システムの初期化
    g.systems = Systems()

if __name__ == '__main__':
    from scene.maingame import Scene_MainGame
    main(Scene_MainGame())
