import math

import pygame

import globals as g
import graphics_ex as gra_ex
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import ShellType, StageId, float_format
from game import Cameraman, Game
from geometry import (Matrix, Transform, create_bounding_box_by_points,
                      rect_to_points)


# python -m trial.camera を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/camera.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_TryCamera(Scene):

    def __init__(self):
        super().__init__()
    
    def prepare(self):
        self.game = Game()

        self.stage_list = StageId.id_list()
        self.stage_index = 0
        
        self.reset_game()
    
    def reset_game(self):
        self.game.load(self.stage_list[self.stage_index])
        
        self.selected_player = self.game.world.player_list[0]
        
        self.selected_player.x = 100
        self.game.cameraman.set_target_entity(self.selected_player)
        self.game.open_sight(self.selected_player)

        w = self.game.world.collision.world_width()
        h = self.game.world.collision.world_height()
        scale = 200 / max(w, h)
        
        self.scale = scale
        self.minimap_rect = pygame.Rect(900, 360, int(w * scale), int(h * scale))
        self.minimap_xys_list = []

        camera = self.game.camera

        self.game.cameraman.neutral()
        camera.x, camera.y = self.game.world.collision.world_rect().midbottom
        
        # メソッドの上書き用
        self.src_method = camera.in_world
        
        m = type(camera.in_world)
        camera.in_world = m(in_world_custom, camera)

    def update(self):
        input_sys = g.systems.input_sys
        # ステージ変更
        if input_sys.is_push(KeyCodes.KEY_1):
            self.stage_index = (self.stage_index + 1) % len(self.stage_list)
            self.reset_game()
            return
        
        # player controls
        cmd = self.selected_player.command
        if (input_sys.is_push(KeyCodes.SPACE)):
            cmd.set_shot(0.5, ShellType.TAKOYAKI) # shot
        if (input_sys.is_keydown(KeyCodes.W)):
            cmd.decrease_shooting_angle()
        if (input_sys.is_keydown(KeyCodes.S)):
            cmd.increase_shooting_angle()
        if (input_sys.is_keydown(KeyCodes.A)):
            cmd.move_left()
        if (input_sys.is_keydown(KeyCodes.D)):
            cmd.move_right()
        
        if (input_sys.is_push(KeyCodes.I)):
            self.game.cameraman.start_intro()
        if (input_sys.is_push(KeyCodes.O)):
            self.game.cameraman.end_intro()
        if (input_sys.is_push(KeyCodes.P)):
            self.toggle_method()
        
        self.game.update()
        if (self.game.cameraman.is_neutral()):
            Cameraman.debug_control(self.game.camera)

        self.update_minimap()
    
    def toggle_method(self):
        camera = self.game.camera
        if camera.in_world != self.src_method:
            camera.in_world = self.src_method
        else:
            m = type(camera.in_world)
            camera.in_world = m(in_world_custom, camera)
    
    def method_name(self):
        return "in_world_custom" if self.game.camera.in_world != self.src_method else "in_world"
    
    def update_minimap(self):
        input_sys = g.systems.input_sys

        # ミニマップのウェイポイントを削除する
        if input_sys.is_push(KeyCodes.N):
            self.minimap_xys_list = []
        # ミニマップをクリックしたら、そのワールド座標を保存する
        if (input_sys.is_push(KeyCodes.MOUSE_LEFT) and self.minimap_rect.collidepoint(*input_sys.mouse_pos)):
            x, y = input_sys.mouse_pos
            self.minimap_xys_list.append((x, y, None))
        # ウェイポイントをカメラマンにセットする
        if (input_sys.is_push(KeyCodes.M) and len(self.minimap_xys_list) != 0):
            waypoint_list = [(*self.minimap_to_world_matrix.transform_point(x, y), s) for x, y, s in self.minimap_xys_list]
            self.game.cameraman.set_waypoint_list(waypoint_list)
        if input_sys.is_push(KeyCodes.L):
            self.game.cameraman.set_target_entity(self.selected_player)
        
        # ミニマップ座標をワールド座標に変換する行列を作成
        mat = Matrix()
        mat.identity()
        mat.translate(-self.minimap_rect.left, -self.minimap_rect.top)
        mat.scale(1/self.scale, 1/self.scale)
        self.minimap_to_world_matrix = mat.clone()
        
        # ワールド座標をミニマップ座標に変換する行列を作成
        self.world_to_minimap_matrix = mat.clone()
        self.world_to_minimap_matrix.invert()
        
        # スクリーン座標からミニマップ座標に変換する行列を作成
        mat.concat(self.game.transform.world_to_screen_matrix)
        self.screen_to_minimap_matrix = mat.clone()
        self.screen_to_minimap_matrix.invert()
    
    def render(self):
    
        g.graphics.fill((160, 192, 255))
        self.game.render()

        camera = self.game.camera
        g.systems.debug_sys.text("camera")
        g.systems.debug_sys.text(f"x={float_format(camera.x)} y={float_format(camera.y)} rot={float_format(camera.rotate_rad)} scale={float_format(camera.scale)}")

        g.systems.debug_sys.text("cameraman")
        g.systems.debug_sys.text(f"mode = {self.game.cameraman.mode}")
        g.systems.debug_sys.text("- controls -")
        g.systems.debug_sys.text("KEY_1: ステージの変更")
        g.systems.debug_sys.text("W, A, S, D, SPACE: プレイヤー操作")
        g.systems.debug_sys.text("I, O: start_intro, end_intro")
        g.systems.debug_sys.text(f"P: メソッドの書き換え 現在のメソッド={self.method_name()}")
        g.systems.debug_sys.text("N:ウェイポイントの削除")
        g.systems.debug_sys.text("M:ウェイポイントへ移動")
        g.systems.debug_sys.text("L:ターゲットモード")

        g.graphics.rectangle(g.BATTLE_SCREEN_RECT, outline=(32, 32, 32))

        self.draw_minimap()

    def draw_minimap(self):
    
        for i, (x, y, scale) in enumerate(self.minimap_xys_list):
            # ミニマップ上に描画
            gra_ex.draw_point_and_label(g.surface, x, y, "target_" + str(i))

        g.graphics.rectangle(self.minimap_rect, outline=(255, 0, 0))
        
        view_points_on_minimap = [self.screen_to_minimap_matrix.transform_point(*point) for point in rect_to_points(g.BATTLE_SCREEN_RECT)]
        view_rect_on_minimap = create_bounding_box_by_points(view_points_on_minimap).to_rect()
        g.graphics.rectangle(view_rect_on_minimap, outline=(0, 0, 255))


# Camera::in_worldをこのメソッドで書き換える
def in_world_custom(self, transform, world_area):
    # スクリーンの４隅を、ワールド座標に変換する
    view_point_list = Transform.create_view_point_list(transform, g.BATTLE_SCREEN_RECT)
    # ワールド座標系のビュー領域から、バウンディングボックスを作成する
    world_view_bbox = create_bounding_box_by_points(view_point_list)
    
    out_of_world, center_x, center_y, scale, _ = Transform.calc_viewarea_in_world2(world_view_bbox, g.BATTLE_SCREEN_RECT.size, world_area)
    
    print(out_of_world, center_x, center_y, scale)
    
    # ワールド領域を超えたら、ワールド領域のなかに収まるビュー領域を再計算する
    if (out_of_world):
        # カメラの更新
        self.x = center_x
        self.y = center_y
        self.scale = scale
        
        # 変換行列の再計算
        transform.calc_transform_from_camera(self.x, self.y, self.rotate_rad, self.scale)

if __name__ == '__main__':
    main.main(Scene_TryCamera(), window_width=1200)
