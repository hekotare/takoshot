import math

import pygame

import globals as g
import graphics_ex as gra_ex
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import ShellType, StageId, float_format
from game import Game
from geometry import Matrix, create_bounding_box_by_points, rect_to_points


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
        
        self.game.cameraman.set_target_entity(self.selected_player)
        self.game.cameraman.user_control = True
        self.game.open_sight(self.selected_player)

        w = self.game.world.collision.world_width()
        h = self.game.world.collision.world_height()
        scale = 200 / max(w, h)
        
        self.scale = scale
        self.minimap_rect = pygame.Rect(720, 300, int(w * scale), int(h * scale))
        self.minimap_xys_list = []
    
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
        
        #self.game.update()
        
        self.game.world.update()
        
        if (self.game.cameraman.is_neutral()):
            Cameraman.debug_control(self.game.camera)
        
        self.game.cameraman.update()
        self.game.camera.update(self.game.transform)

        self.update_minimap()
    
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

# カメラ操作クラス
class Cameraman:
    MODE_WAIT = "wait"
    MODE_TARGET = "target"
    MODE_WAYPOINT = "waypoint"

    @classmethod
    def create_view_rect(cls, x, y, scale):
    
        rect = g.BATTLE_SCREEN_RECT.copy()
        
        rect.width  *= scale
        rect.height *= scale
        
        rect.center = (x, y)
        
        return rect
    
    @classmethod
    def move_camera_to(cls, camera, x, y, scale = None, velocity = 0.05):
        cls.move_camera(camera, x - camera.x, y - camera.y,
                    None if (scale is None) else scale - camera.scale, velocity)
    
    # velocity ～1.0
    @classmethod
    def move_camera(cls, camera, dx, dy, scale = None, velocity = 0.05):
        camera.x += dx * velocity
        camera.y += dy * velocity
        
        if (scale is not None):
            camera.scale += scale * velocity
    
    # デバッグ用のカメラ操作
    @classmethod
    def debug_control(self, camera):
        input_sys = g.systems.input_sys
        if (input_sys.is_keydown(KeyCodes.NUMPAD1)):
            camera.x -= 2
        if (input_sys.is_keydown(KeyCodes.NUMPAD3)):
            camera.x += 2
        if (input_sys.is_keydown(KeyCodes.NUMPAD5)):
            camera.y -= 2
        if (input_sys.is_keydown(KeyCodes.NUMPAD2)):
            camera.y += 2
        if (input_sys.is_keydown(KeyCodes.NUMPAD4)):
            camera.scale = max(0.01, camera.scale - 0.02)
        if (input_sys.is_keydown(KeyCodes.NUMPAD6)):
            camera.scale += 0.02
        if (input_sys.is_keydown(KeyCodes.NUMPAD7)):
            camera.rotate_rad -= math.pi * 0.05
        if (input_sys.is_keydown(KeyCodes.NUMPAD9)):
            camera.rotate_rad += math.pi * 0.05
        if (input_sys.is_keydown(KeyCodes.NUMPAD8)):
            camera.scale = 1.0
            camera.rotate_rad = 0.0

    def __init__(self, game):
        self.game = game
        self.mode = self.MODE_WAIT
        self.target_entity = None

    # ウェイポイントへカメラを移動する
    # waypoint_list: タプル（x, y) or（x, y, scale)のリスト
    def set_waypoint_list(self, waypoint_list):
    
        self.mode = self.MODE_WAYPOINT
        list = []
        
        # 要素数をそろえる
        for waypoint in waypoint_list:
            if (len(waypoint) == 2):
                list.append((*waypoint, None))
            elif (len(waypoint) == 3):
                list.append(waypoint)
            else:
                assert False, f"waypoint len={len(waypoint)}"
        
        self.waypoint_list = list
        self.set_next_waypoint()
    
    def set_target_entity(self, entity, velocity = 0.05):
        self.mode = self.MODE_TARGET
        self.target_entity = entity
        self.target_velocity = velocity

    def set_next_waypoint(self):
        x, y, scale = self.waypoint_list.pop(0)
        view_rect = self.create_view_rect(x, y, scale or self.game.camera.scale)
        out_of_world, ofs_scale, ofs_x, ofs_y = self.game.transform.calc_viewarea_in_world(view_rect, self.game.camera.range_of_viewarea)
        
        # 移動後にビュー領域がワールドからはみ出る場合は、移動データを修正してはみ出ないようにする
        if (out_of_world):
            self.waypoint_x = x + ofs_x
            self.waypoint_y = y + ofs_y
            
            if (scale is None):
                self.waypoint_scale = None
            else:
                self.waypoint_scale = scale * ofs_scale
        else:
            self.waypoint_x, self.waypoint_y, self.waypoint_scale = x, y, scale
    
    def update(self):
        if self.mode == self.MODE_TARGET:
            self.update_target()
        elif self.mode == self.MODE_WAYPOINT:
            self.update_waypoint()
    
    def update_target(self):
        self.move_camera_to(self.game.camera, self.target_entity.x, self.target_entity.y, None, self.target_velocity)

    def update_waypoint(self):
        self.move_camera_to(self.game.camera, self.waypoint_x, self.waypoint_y, self.waypoint_scale)
        dist = max(abs(self.waypoint_x - self.game.camera.x), abs(self.waypoint_y - self.game.camera.y))
        
        if (dist <= 0.5):
            if (len(self.waypoint_list) != 0):
                self.set_next_waypoint()
            else:
                # すべてのポイントに移動した！
                self.mode = self.MODE_WAIT

if __name__ == '__main__':
    main.main(Scene_TryCamera(), window_width=1200)
