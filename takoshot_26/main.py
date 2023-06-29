import sys

import pygame

import globals as g
import graphics
import graphics_ex as gra_ex
from core.scene import Scene_Container
from core.systems import Systems
from data.bitmap_data import BitmapDataManager
from data.character_data import ChrDataManager
from data.sound_data import SoundDataManager
from data.stage_data import StageDataManager
from defines import *

surface = None

def main(type_or_scene_factory, window_width=None, window_height=None):

    systems = systems_init(window_width=window_width, window_height=window_height)


    root = Scene_Container(systems, SceneId.ROOT)
    root.add_child(type_or_scene_factory())
    
    clock = pygame.time.Clock()

    while(True):
        
        systems.begin_process()
        
        surface.fill((0, 0, 0))
        g.graphics.fill((0, 0, 0))

        # シーンの更新
        root.update()
        root.render()

        # シーン名を描画（とりあえずここに追加）
        if (g.DebugFlags.DISPLAY_SCENE_ID):
            gra_ex.draw_scene_id(root)

        debug_render()

        # fpsの描画
        g.graphics.text((g.WINDOW_RECT.right - 60, 0),
                        str(round(clock.get_fps(), 2)), (255, 255, 255), background=(0, 0, 0))
        
        surface.blit(g.surface, (0, 0))
        
        pygame.display.update()
        
        systems.end_process()
        
        clock.tick(FPS)
        
        # event
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # とりあえずこれでいい？
            if event.type == pygame.MOUSEWHEEL:
                systems.input_sys.on_mousewheel_delta(event.y) # ホイールの移動量

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
    
    res_sys = ResourceSys()

    # システムの初期化
    g.systems = Systems(res_sys, FPS)

    return g.systems

def debug_render():
    systems = g.systems
    debug_sys = g.systems.debug_sys

    if (g.DebugFlags.DISPLAY_CURRENT_MOUSE_TARGET and systems.mouse_target_sys.has_mouse_target()):
        t = systems.time_sys.cos_wave(2000) # 0～1
        g.graphics.rectangle(systems.mouse_target_sys.current_target_rect, outline=(128 + 127 * t, 128, 128), width = 4)
        debug_sys.text(f"mouse_target_id={systems.mouse_target_sys.current_target_id}")
    
    for i, text_param in enumerate(debug_sys.text_param_list):
        args, kwargs = text_param

        # 上書き
        kwargs['font'] = g.font_16
        kwargs['background'] = (0, 0, 0)

        # テキストカラー指定がなかった場合は、デフォルトで白にする
        if (len(args) == 1): args = (args[0], (255, 255, 255))
        
        g.graphics.text((debug_sys.x, debug_sys.y + i * 30), *args, **kwargs)

# ゲームのリソースを追加
class ResourceSys:

    def init(self):
        self.bitmap = BitmapDataManager()
        self.bitmap.load()

        self.sound = SoundDataManager()
        self.sound.load()

        self.chrdata = ChrDataManager()
        self.chrdata.load()

        self.stage = StageDataManager()
        self.stage.load(self.bitmap)

if __name__ == '__main__':
    from scene.menu import Scene_GameRoot
    main(Scene_GameRoot)