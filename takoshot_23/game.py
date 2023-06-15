import math
import random

import globals as g
import graphics_ex as gra_ex
from core.input_sys import KeyCodes
from defines import MouseTargetId, clamp
from entity.world import World
from geometry import Transform, create_bounding_box_by_points


class Game:

    def __init__(self):
        self.sight = Sight()
        self.sight_player = None
        self.transform = Transform(g.BATTLE_SCREEN_RECT)
    
    def load(self, stage_id):
        self.create_world(stage_id)

        p_list = self.world.stage.create_start_point_list()
        p_list = random.sample(p_list, 2)
        self.world.add_player(*p_list[0])
        self.world.add_player(*p_list[1])
    
    def create_world(self, stage_id):
        self.world = World(stage_id)
        self.camera = Camera(self.world.collision.world_rect())
        self.cameraman = Cameraman(self)
    
    def update(self):
        self.world.update()
        self.cameraman.update()
        self.camera.update(self.transform)

    def render(self):
    
        gra_ex.draw_battle_background()
        
        world = self.world
        
        gra_ex.draw_stage(world.stage, self.transform)
        
        # キャラクタの照準
        self.sight.update()
        
        gra_ex.draw_player_sight(self.sight_player, self.sight.scale, self.transform)
        
        for player in world.player_list:
            gra_ex.draw_player(player, self.transform)
            gra_ex.draw_player_status(player, self.transform)
        
        for shell in world.shell_list:
            gra_ex.draw_shell(shell, self.transform)
        
        # エフェクト
        for eff in self.world.effect_list:
            eff.render(self)
        
        #---------------------------------
        # debug
        #---------------------------------
        if g.DebugFlags.DISPLAY_PLAYER_MUZZLE_POSITION:
            for player in self.world.player_list:
                gra_ex.draw_player_muzzle_position(g.surface, player, self.transform)
    
    # 試合が決着しているか判定する
    def check_game_finished(self):
    
        # 生存者チェック
        alive_players = [player for player in self.world.player_list if player.is_alive()]
        num_of_alive = len(alive_players)
        
        if (num_of_alive in [0, 1]): # 全員死亡した or 一人が生き残った
            return True, alive_players
        
        return False, []

    def open_sight(self, player):
        self.sight.open()
        self.sight_player = player

    def close_sight(self):
        self.sight.close()

# プレイヤーの照準
class Sight:

    class State:
        Opening = "opening"
        Open    = "open"
        Closing = "closing"
        Closed  = "closed"
    
    def __init__(self):
        self.player = None
        self.state = self.State.Closed
        self.scale = 0.0
        self.timer = g.systems.time_sys.create_sys_timer()
    
    def open(self):
        self.state = self.State.Opening
        self.timer.start(duration_time_ms=250)
    
    def close(self):
        self.state = self.State.Closing
        self.timer.start(duration_time_ms=250)

    def update(self):
        if (self.state == self.State.Opening):
        
            if (self.timer.is_finished()):
                self.state = self.State.Open

            self.scale = self.timer.progress
            
        elif (self.state == self.State.Closing):
        
            if (self.timer.is_finished()):
                self.state = self.State.Closed
            
            self.scale = 1.0 - self.timer.progress

# カメラ
class Camera:

    def __init__(self, world_rect):
        self.x = 0
        self.y = 0
        self.rotate_rad = 0
        self.scale = 1.0
        
        # カメラの移動できる境界は、ワールド境界より少しだけ内側に設定しておく（ワールドの外側が表示されないようになると良いなぁ）
        self.range_of_viewarea = world_rect.inflate(-10, -10)
    
    def clamp(self):
        self.scale = clamp(self.scale, 0.2, 4) # スケールの限界を設定
    
    def update(self, transform):
        self.clamp()
        
        transform.calc_transform_from_camera(self.x, self.y, self.rotate_rad, self.scale)
        self.in_world(transform, self.range_of_viewarea)
        
        self.clamp()
    
    def in_world(self, transform, world_area):
        # スクリーンの４隅を、ワールド座標に変換する
        view_point_list = Transform.create_view_point_list(transform, g.BATTLE_SCREEN_RECT)
        # ワールド座標系のビュー領域から、バウンディングボックスを作成する
        world_view_bbox = create_bounding_box_by_points(view_point_list)
        
        out_of_world, center_x, center_y, scale, _ = Transform.calc_viewarea_in_world2(world_view_bbox, g.BATTLE_SCREEN_RECT.size, world_area)
        
        # ワールド領域を超えたら、ワールド領域のなかに収まるビュー領域を再計算する
        if (out_of_world):
            # カメラの更新
            self.x = center_x
            self.y = center_y
            self.scale = scale
            
            # 変換行列の再計算
            transform.calc_transform_from_camera(self.x, self.y, self.rotate_rad, self.scale)


# カメラ操作クラス
class Cameraman:
    MODE_MANUAL = "neutral"
    MODE_TARGET = "target"
    MODE_WAYPOINT = "waypoint"
    MODE_WAYPOINT_FINISHED = "waypoint_finished"
    
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
        self.mode = self.MODE_MANUAL
        self.target_entity = None
    
    # イントロ開始時のカメラ設定
    def start_intro(self):
        game = self.game
        
        game.camera.scale = 2
        self.set_waypoint_list(
                [(player.x, player.y, 1.0) for player in game.world.player_list]) # プレイヤーのxy座標リスト
    
    # イントロが終了し、ユーザーがカメラを動かせるようにする
    def end_intro(self):
        self.neutral()
    
    def neutral(self):
        self.mode = self.MODE_MANUAL
    
    def is_neutral(self):
        return self.mode == self.MODE_MANUAL
    
    def is_intro_finished(self):
        return self.mode == self.MODE_WAYPOINT_FINISHED

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
    
    # 消極的にターゲット設定を行う
    def passive_target_entity(self, entity, velocity = 0.05):
        if (self.mode == self.MODE_TARGET):
            self.set_target_entity(entity, velocity)

    def set_next_waypoint(self):
        x, y, scale = self.waypoint_list.pop(0)
        view_rect = self.create_view_rect(x, y, scale or self.game.camera.scale)
        out_of_world, x, y, s, _ = self.game.transform.calc_viewarea_in_world2(view_rect, g.BATTLE_SCREEN_RECT.size, self.game.camera.range_of_viewarea)
        
        # 移動後にビュー領域がワールドからはみ出る場合は、移動データを修正してはみ出ないようにする
        if (out_of_world):
            self.waypoint_x = x
            self.waypoint_y = y
            
            if (scale is None):
                self.waypoint_scale = None
            else:
                self.waypoint_scale = s
        else:
            self.waypoint_x, self.waypoint_y, self.waypoint_scale = x, y, scale
    
    def update(self):
    
        if (self.mode == self.MODE_MANUAL):
            self.user_controls()
        
        if self.mode == self.MODE_TARGET:
        
            # ユーザー操作が挟まったらターゲットを終了
            if self.user_controls():
                self.neutral()
                return

            self.update_target(self.target_velocity)
        
        elif self.mode == self.MODE_WAYPOINT:
            self.update_waypoint()
    
    def user_controls(self):
        
        ret = False
        input_sys = g.systems.input_sys
        camera = self.game.camera
        
        if g.systems.mouse_target_sys.current_target_id != MouseTargetId.MAINGAME: return
        
        #----------------------------------------------------------------
        # マウスの左ボタンが押されていたらカメラを移動
        #----------------------------------------------------------------
        if (input_sys.is_keydown(KeyCodes.MOUSE_LEFT)):
            x0, y0 = self.game.transform.screen_to_world(*input_sys.mouse_pos)
            x1, y1 = self.game.transform.screen_to_world(*g.BATTLE_SCREEN_RECT.center)
            self.move_camera(self.game.camera, x0 - x1, y0 - y1)

            ret = True
        
        #----------------------------------------------------------------
        # マウスの真ん中ボタンでカメラのズーム
        #----------------------------------------------------------------
        if (input_sys.delta != 0):
        
            camera.scale += (input_sys.delta * 0.05)
            
            if self.mode == self.MODE_MANUAL:
                x, y = self.game.transform.screen_to_world(*input_sys.mouse_pos)
                self.move_camera_to(self.game.camera, x, y, None, 0.2)
            if self.mode == self.MODE_TARGET:
                self.update_target(1.0)
        
        return ret

    # velocity  0.0 < velocity <= 1.00
    def update_target(self, velocity):
        self.move_camera_to(self.game.camera, self.target_entity.x, self.target_entity.y, None, velocity)

    def update_waypoint(self):
        self.move_camera_to(self.game.camera, self.waypoint_x, self.waypoint_y, self.waypoint_scale)
        dist = max(abs(self.waypoint_x - self.game.camera.x), abs(self.waypoint_y - self.game.camera.y))
        
        if g.DebugFlags.PRINT_update_waypoint and (dist < 10):
            print(f"update_waypoint dist={dist}")
        
        if (dist <= 0.5):
            if (len(self.waypoint_list) != 0):
                self.set_next_waypoint()
            else:
                # すべてのポイントに移動した！
                self.mode = self.MODE_WAYPOINT_FINISHED
