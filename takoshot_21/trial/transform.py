import math

import pygame

import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from geometry import Transform, create_bounding_box_by_points


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
    
    
    def render(self):
    
        g.graphics.fill((224, 224, 224))
        
        # 点滅させたいやつにテキトーに使う
        t = g.systems.time_sys.cos_wave(250)
        flash_color = 128 + t * 127
        
        tako_img = g.systems.res_sys.bitmap.get_bitmap('chr001', 0)
        
        #######################################
        # ワールド座標系の描画
        #######################################
        world = self.world
        
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
        
        # スクリーン領域の中心
        rect = pygame.Rect(screen.area)
        g.graphics.circle((rect.centerx, rect.centery), 2, fill=(0, 160, 0), outline=(20, 20, 20), width = 2)

        # キャラクタ
        g.graphics.circle((screen.chr_x, screen.chr_y), screen.chr_radius, fill=(0, flash_color, 0))
        
        # タコ
        g.graphics.blit2(tako_img, (screen.tako_x, screen.tako_y), screen.tako_scale, screen.tako_rotate_deg, (0.5, 0.75))
        
        # スクリーン領域
        g.graphics.rectangle(screen.area, outline=(0, 160, 0), width = 2)
        g.graphics.text((screen.area[0] + screen.area[2] * 0.5, 20), "[Screen Area]", (0, 160, 0), textalign="center")

        # center
        rect = pygame.Rect(screen.area)
        g.graphics.circle((rect.centerx, rect.centery), 2, fill=(0, 160, 0), outline=(20, 20, 20), width = 2)

        #######################################
        # 操作説明
        #######################################
        debug_sys = g.systems.debug_sys
        debug_sys.x = 1200
        debug_sys.text("- controls -")
        debug_sys.text("カメラの移動   W A S D")
        debug_sys.text("カメラのズーム Q E")
        debug_sys.text("カメラの回転   R T")
        debug_sys.text("キャラクターの移動 UP, DOWN, LEFT, RIGHT")
        
        debug_sys.text("タコの移動    B H N M")
        debug_sys.text("タコの回転    U I")
        debug_sys.text("タコの大きさ  J K")

if __name__ == '__main__':
    main.main(Scene_TryTransform(), window_width=1600, window_height=800)
