import math

import pygame

import globals as g
import graphics as gra
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from geometry import Geometry


#
# グラフィックの回転をテスト
#
# python -m trial.blit_rotate を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/blit_rotate.pyを入力し、リモートデバッグ実行
class Scene_TryRotate(Scene):

    exp_list = [
        "画像をblitで描画、プレイヤー座標の右下に描画される",
        "pygame.transform.rotateで画像を回転させてからblitで描画",
        "回転させた画像の真ん中を中心にして描画してみる",
        "ズレを修正する",
        "rotate_blit 画像の足元付近を中心にしてみる",
        "rotate_blit 画像の右下を中心にしてみる",
    ]
    
    def __init__(self):
        super().__init__(g.systems)
    
    def prepare(self):
        self.angle = 0
        self.step = 0
        self.move = True
        self.surf = pygame.image.load('res/image/blit_rotate_test.png').convert_alpha()
    
    def update(self):
    
        if (self.move):
            self.angle += 2
        if (g.systems.input_sys.is_push(KeyCodes.Z)):
            self.angle = 0
        
        if (g.systems.input_sys.is_push(KeyCodes.KEY_1)):
            self.step = (self.step + 1) % len(self.exp_list)
        if (g.systems.input_sys.is_push(KeyCodes.KEY_2)):
            self.step = (self.step - 1) % len(self.exp_list)
        if (g.systems.input_sys.is_push(KeyCodes.KEY_3)):
            self.move = not self.move
    
    def render(self):
        
        surf = self.surf
        g.graphics.fill((255, 255, 255))
        
        # プレイヤーの座標
        pos = (150, 150)

        c = g.systems.time_sys.cos_wave(1000)
        c = (c + 1) * 0.5 # 0.0 ~ 1.0
        c = int(127 * c)
        point_color = (128 + c, 64 + c, 64 + c)

        # ふつうにキャラクタの画像を描画
        # 画像の左上が中心となる
        if (self.step == 0):
            g.graphics.blit(surf, pos)
        
        # 回転した画像をそのまま描画
        # 回転後の画像は回転前より大きくなる
        elif (self.step == 1):
            rotated_surf = pygame.transform.rotate(surf, self.angle)
            gra.rectangle(rotated_surf, rotated_surf.get_rect(), outline=(0, 0, 0))
            g.graphics.blit(rotated_surf, pos)
        
        # 回転した画像の真ん中が中心となるように描画
        # 中心にしたい座標は、その座標と画像の真ん中の距離分だけずれている
        elif (self.step == 2):
            rotated_surf = pygame.transform.rotate(surf, self.angle)
            gra.rectangle(rotated_surf, rotated_surf.get_rect(), outline=(0, 0, 0))

            g.graphics.blit(rotated_surf, (pos[0] - rotated_surf.get_width() * 0.5, pos[1] - rotated_surf.get_height() * 0.5))

        #
        elif (self.step == 3):
            
            # オフセット値の計算
            rad = -math.radians(self.angle) # pygame.transfate.rotateとGeometry.rotateの回転方向が逆なので、マイナス
            x0, y0 = surf.get_width() * 0.5, surf.get_height() * 0.5  # 画像の真ん中
            x1, y1 = surf.get_width() * 0.5, surf.get_height() * 0.75
            ofs_x, ofs_y = Geometry.rotate(x1-x0, y1-y0, rad)
            
            # 画像を回転
            rotated_surf = pygame.transform.rotate(surf, self.angle)
            gra.rectangle(rotated_surf, rotated_surf.get_rect(), outline=(0, 0, 0)) # わかりやすいように枠を描画

            # 描画
            g.graphics.blit(rotated_surf, (pos[0] - rotated_surf.get_width() * 0.5 - ofs_x, pos[1] - rotated_surf.get_height() * 0.5 - ofs_y))

        elif (self.step == 4):
            # 任意の座標を中心にして回転描画できる
            rotate_blit(surf, pos, (surf.get_width() * 0.5, surf.get_height() * 0.75), self.angle)
        
        elif (self.step == 5):
            # 任意の座標を中心にして回転描画できる その２
            rotate_blit(surf, pos, (surf.get_width() - 1, surf.get_height() - 1), self.angle)
        
        g.graphics.circle(pos, 4, fill=point_color, outline=(20, 20, 20))

        g.graphics.text((20, 40), self.exp_list[self.step], (255, 255, 255), background=(0, 0, 0))

def rotate_blit(surf, dist_pos, origin_pos, angle_degree):
    # オフセット値の計算
    rad = -math.radians(angle_degree) # pygame.transfate.rotateとGeometry.rotateの回転方向が逆なので、マイナス
    x0, y0 = surf.get_width() * 0.5, surf.get_height() * 0.5  # 画像の真ん中
    x1, y1 = origin_pos # 任意の中心点
    ofs_x, ofs_y = Geometry.rotate(x1-x0, y1-y0, rad)
    
    # 画像を回転
    rotated_surf = pygame.transform.rotate(surf, angle_degree)

    # 描画
    g.graphics.blit(rotated_surf, (dist_pos[0] - rotated_surf.get_width() * 0.5 - ofs_x, dist_pos[1] - rotated_surf.get_height() * 0.5 - ofs_y))

if __name__ == '__main__':
    main.main(Scene_TryRotate)
