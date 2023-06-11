import math

import pygame

import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from geometry import (Matrix, Transform, create_bounding_box_by_points,
                      rect_to_points)


# graphicsのblitと比較するためにローカルで実装
def blit_custom(src_img, pos, scale, angle_deg, origin_pos, **kwargs):
    clip_rect = kwargs.get('clip_rect')
    
    if (clip_rect):
        img, origin_x, origin_y, _ = clipping_img(src_img, pos, scale, angle_deg, origin_pos, clip_rect)
    else:
        img, origin_x, origin_y = src_img, src_img.get_width() * origin_pos[0], src_img.get_height() * origin_pos[1]
    
    scaled_img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
    g.graphics.rotate_blit(scaled_img, pos, (origin_x, origin_y), angle_deg, **kwargs)

def clipping_img(img, pos, scale, angle_deg, origin_pos, clipping_rect):

    # screen to surface_local matrix
    mat = Matrix()
    mat.translate(-img.get_width() * origin_pos[0], -img.get_height() * origin_pos[1]) # to surface_origin
    mat.scale(scale, scale)
    mat.rotate(-math.radians(angle_deg)) # pygame.transform.rotateのプラス値は反時計回りでMatrixクラスと逆回転なので、マイナス値を入力する
    mat.translate(*pos)
    mat.invert()
    
    # スクリーンの四隅の座標を、サーフェイスのローカル座標系に変換する
    points = rect_to_points(pygame.Rect(clipping_rect))
    points = [mat.transform_point(x, y) for x, y in points]
    
    # スクリーンの四隅の座標（サーフェイスローカル座標系）から、サーフェイスの切り取り範囲を計算する
    rect = create_bounding_box_by_points(points).to_rect()
    rect = rect.clip(img.get_rect()) # グラフィックの切り取り領域を取得
    
    cliped_img = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    cliped_img.blit(img, (0, 0), rect)
    
    # 中心座標を再計算
    origin_x = (img.get_width() * origin_pos[0] - rect.left) * scale
    origin_y = (img.get_height() * origin_pos[1] - rect.top) * scale

    return cliped_img, origin_x, origin_y, {'clipping_rect':rect, 'screen_points':points}

# python -m trial.transform を入力し実行
# python -m debugpy --wait-for-client --listen 5678 try/try_transform.py を入力し、リモートデバッグ実行
class Scene_TryTransform(Scene):

    class Screen:
        def __init__(self):
            # スクリーン座標系の領域
            self.area = (20, 20, 320, 240)
            # キャラクタ
            self.chr_x = 0
            self.chr_y = 0
            self.chr_radius = 0
            # タコ
            self.tako_x = 0
            self.tako_y = 0
            self.tako_rotate_deg = 0
            self.tako_scale = 1.0
    
    class World:
        def __init__(self):
            # ワールド座標系の領域
            self.area = (400, 100, 640, 480)
            # カメラ
            self.camera_x = 400 + 340
            self.camera_y = 100 + 220
            self.camera_scale = 1
            self.camera_rotate_rad = 0.0
            # キャラクタ
            self.chr_x = 400 + 500
            self.chr_y = 100 + 300
            self.chr_radius = 12
            # タコ
            self.tako_x = 400 + 200
            self.tako_y = 100 + 100
            self.tako_rotate_deg = 0
            self.tako_scale = 1.0
    
    def prepare(self):
        self.screen = self.Screen()
        self.world = self.World()

        # 描画関数
        self.clip_func_index = 0
        self.clip_func_list = [
            [g.graphics.blit2, "Graphics.blit2"],
            [g.graphics.blit3, "Graphics.blit3"],
            [blit_custom, "blit_custom"]
        ]
        
        self.transform = Transform(self.screen.area)
    
    def update(self):
        # ワールドのキャラクタ、カメラを操作
        self.control_world()

        # ワールドのカメラから、変換行列を作成
        self.transform.calc_transform_from_camera(self.world.camera_x, self.world.camera_y, self.world.camera_rotate_rad, self.world.camera_scale)

        ############################################
        # スクリーン座標系のキャラクタを更新
        ############################################
        # circle
        self.screen.chr_x, self.screen.chr_y, _, self.screen.chr_radius = self.transform.world_to_screen(self.world.chr_x, self.world.chr_y, 0, self.world.chr_radius)
        
        # タコ
        self.screen.tako_x, self.screen.tako_y, self.screen.tako_rotate_deg, self.screen.tako_scale = \
            self.transform.world_to_screen(self.world.tako_x, self.world.tako_y, self.world.tako_rotate_deg, self.world.tako_scale)
        
        ############################################
        # 描画される範囲をワールド座標系に書き込む
        ############################################
        screen_rect = pygame.Rect(self.screen.area)
        xx = screen_rect.left + screen_rect.width * 0.7
        yy = screen_rect.top + screen_rect.height * 0.3
        
        # スクリーン矩形をワールド座標に変換して、ワールドに描き込んでみる
        self.world.view_point_list = Transform.create_view_point_list(self.transform, screen_rect)
        
        # ワールド座標系のビュー領域から、バウンディングボックスを作成する
        world_view_bbox = create_bounding_box_by_points(self.world.view_point_list)
        
        self.world.camera_head = self.transform.screen_to_world(screen_rect.centerx, yy)
        self.world.camera_side = self.transform.screen_to_world(xx, screen_rect.centery)
        self.world.camera_bbox = world_view_bbox

        # ビュー領域がワールド領域を超えているかチェックする
        # ワールド領域を超えていたらビュー領域のズーム、座標を調整して超えないようにする
        out_of_world, scale, ofs_x, ofs_y = Transform.calc_viewarea_in_world(world_view_bbox, pygame.Rect(*self.world.area))
        
        # ワールド領域を超えたら、ワールド領域のなかに収まるビュー領域を再計算する
        if (out_of_world):
            new_transform = Transform(self.screen.area)
            new_x = self.world.camera_x + ofs_x
            new_y = self.world.camera_y + ofs_y
            new_rot = self.world.camera_rotate_rad
            new_scale = self.world.camera_scale * scale
            new_transform.calc_transform_from_camera(new_x, new_y, new_rot, new_scale)
            
            self.world.view_point_list2 = Transform.create_view_point_list(new_transform, screen_rect)
        
        else:
            self.world.view_point_list2 = []
    
    def control_world(self):
    
        # camera
        if (g.systems.input_sys.is_keydown(KeyCodes.W)):
            self.world.camera_y -= 1
        elif (g.systems.input_sys.is_keydown(KeyCodes.S)):
            self.world.camera_y += 1
        if (g.systems.input_sys.is_keydown(KeyCodes.A)):
            self.world.camera_x -= 1
        elif (g.systems.input_sys.is_keydown(KeyCodes.D)):
            self.world.camera_x += 1
        if (g.systems.input_sys.is_keydown(KeyCodes.Q)):
            self.world.camera_scale -= 0.01
            if (self.world.camera_scale < 0.01): self.world.camera_scale = 0.01
        elif (g.systems.input_sys.is_keydown(KeyCodes.E)):
            self.world.camera_scale += 0.01
        if (g.systems.input_sys.is_keydown(KeyCodes.R)):
            self.world.camera_rotate_rad -= math.pi / 50
        elif (g.systems.input_sys.is_keydown(KeyCodes.T)):
            self.world.camera_rotate_rad += math.pi / 50
        
        # chr
        if (g.systems.input_sys.is_keydown(KeyCodes.UP)):
            self.world.chr_y -= 1
        elif (g.systems.input_sys.is_keydown(KeyCodes.DOWN)):
            self.world.chr_y += 1
        if (g.systems.input_sys.is_keydown(KeyCodes.LEFT)):
            self.world.chr_x -= 1
        elif (g.systems.input_sys.is_keydown(KeyCodes.RIGHT)):
            self.world.chr_x += 1
        
        # tako
        if (g.systems.input_sys.is_keydown(KeyCodes.B)):
            self.world.tako_x -= 1
        if (g.systems.input_sys.is_keydown(KeyCodes.M)):
            self.world.tako_x += 1
        if (g.systems.input_sys.is_keydown(KeyCodes.H)):
            self.world.tako_y -= 1
        if (g.systems.input_sys.is_keydown(KeyCodes.N)):
            self.world.tako_y += 1
        if (g.systems.input_sys.is_keydown(KeyCodes.J)):
            self.world.tako_scale -= 0.01
        if (g.systems.input_sys.is_keydown(KeyCodes.K)):
            self.world.tako_scale += 0.01
        if (g.systems.input_sys.is_keydown(KeyCodes.U)):
            self.world.tako_rotate_deg += 3.5
        if (g.systems.input_sys.is_keydown(KeyCodes.I)):
            self.world.tako_rotate_deg -= 3.5

        # 描画関数を切り替える
        if (g.systems.input_sys.is_push(KeyCodes.KEY_1)):
            self.clip_func_index = (self.clip_func_index + 1) % len(self.clip_func_list)
        
    def render(self):
    
        g.graphics.fill((224, 224, 224))
        
        # 点滅させたいやつにテキトーに使う
        t = g.systems.time_sys.cos_wave(250)
        flash_color = 128 + t * 127
        
        tako_img = g.systems.res_sys.bitmap.get_bitmap('chr001', 0)
        stage_img = g.systems.res_sys.bitmap.get_bitmap('stage', 1)

        #######################################
        # ワールド座標系の描画
        #######################################
        world = self.world
        
        # stage
        g.graphics.blit2(stage_img, (world.area[0], world.area[1]), 1.0, 0, (0, 0))
        
        # ワールド領域
        g.graphics.rectangle(world.area, outline=(0, 0, 160), width= 2)
        g.graphics.text((world.area[0] + 20, world.area[1] + 20), "[World Area]", (0, 0, 160))
        
        # キャラクタ
        g.graphics.circle((world.chr_x, world.chr_y), world.chr_radius, fill=(flash_color, 0, 0))
        g.graphics.text((world.chr_x, world.chr_y + 20), "(chr)", (flash_color, 0, 0), font=g.font_10)
        
        # タコ
        g.graphics.blit2(tako_img, (world.tako_x, world.tako_y), world.tako_scale, world.tako_rotate_deg, (0.5, 0.75))
        
         # ワールドにビュー領域を描画
        g.graphics.polygon(world.view_point_list, outline=(0, 255, 255), width=2)
        
        # カメラ
        g.graphics.rectangle(world.camera_bbox.to_rect(), outline=(255, 128, 128), width=1)
        
        g.graphics.rectangle((world.camera_x - 6, world.camera_y - 6, 12, 12), fill=(0, 0, 255))
        g.graphics.text((world.camera_x, world.camera_y + 20), "(camera)", (0, 0, flash_color), font=g.font_10)
        g.graphics.text((world.camera_x, world.camera_y + 40), f"scale={round(world.camera_scale, 3)}", (20, 20, 20), font=g.font_10)
        
        g.graphics.line((255, 0, 0), (world.camera_x, world.camera_y), world.camera_head)
        g.graphics.line((0, 255, 0), (world.camera_x, world.camera_y), world.camera_side)
        # ワールドに修正後のビュー領域を描画
        if (len(world.view_point_list2) != 0):
            g.graphics.polygon(world.view_point_list2, outline=(64, 192, 128), width=1)
        
        #######################################
        # スクリーン座標系の描画
        #######################################
        screen = self.screen
        blit_func = self.clip_func_list[self.clip_func_index][0]
        
        # stage
        x, y, r, s = self.transform.world_to_screen(self.world.area[0], self.world.area[1], 0, 1.0)
        blit_func(stage_img, (x, y), s, r, (0, 0), clip_rect = screen.area)

        # キャラクタ
        g.graphics.circle((screen.chr_x, screen.chr_y), screen.chr_radius, fill=(0, flash_color, 0))
        
        # タコ
        blit_func(tako_img, (screen.tako_x, screen.tako_y), screen.tako_scale, screen.tako_rotate_deg, (0.5, 0.75), clip_rect = screen.area)
        
        # スクリーン領域
        g.graphics.rectangle(screen.area, outline=(0, 160, 0), width = 2)
        g.graphics.text((screen.area[0] + screen.area[2] * 0.5, 20), "[Screen Area]", (0, 160, 0), textalign="center")

        # center
        rect = pygame.Rect(screen.area)
        g.graphics.circle((rect.centerx, rect.centery), 2, fill=(0, 160, 0), outline=(20, 20, 20), width = 2)
        
        #######################################
        # サーフェイスローカルの描画
        #######################################
        sl_origin = pygame.Vector2(20, 400)
        # サーフェイス全体の描画
        g.graphics.blit(tako_img, sl_origin)
        g.graphics.rectangle((sl_origin.x, sl_origin.y, tako_img.get_width(), tako_img.get_height()), outline=(0, 160, 255), width = 2)
        g.graphics.text(sl_origin + (6, -20), "[surface local]", (0, 160, 255),font = g.font_10)
        
        cliped_img, _, _, info = clipping_img(tako_img, (screen.tako_x, screen.tako_y),
                                        screen.tako_scale, screen.tako_rotate_deg, (0.5, 0.75), screen.area)
        
        screen_points = [sl_origin + (x, y) for x, y in info['screen_points']]
        g.graphics.polygon(screen_points, outline=(255, flash_color, 224), width=3)
        
        clipping_points = [sl_origin + (x, y) for x, y in rect_to_points(info['clipping_rect'])]
        g.graphics.polygon(clipping_points, outline=(255, 160, 0), width = 2)
        # 切り抜いたグラフィックを描画
        g.graphics.blit(cliped_img, sl_origin + (0, 100))
        g.graphics.rectangle((sl_origin.x, sl_origin.y + 100, cliped_img.get_width(), cliped_img.get_height()), outline=(255, 0, 160), width = 1)

        #######################################
        # 操作説明
        #######################################
        debug_sys = g.systems.debug_sys
        debug_sys.x = 1200

        debug_sys.text("- controls -")
        debug_sys.text(f"描画関数の切り替え KEY_1  {self.clip_func_list[self.clip_func_index][1]}")
        debug_sys.text("")
        debug_sys.text("カメラの移動   W A S D")
        debug_sys.text("カメラのズーム Q E")
        debug_sys.text("カメラの回転   R T")
        debug_sys.text("キャラクターの移動 UP, DOWN, LEFT, RIGHT")
        debug_sys.text("")
        debug_sys.text("タコの移動    B H N M")
        debug_sys.text("タコの回転    U I")
        debug_sys.text("タコの大きさ  J K")
        debug_sys.text("------------------------")

if __name__ == '__main__':
    main.main(Scene_TryTransform(), window_width=1600, window_height=800)
