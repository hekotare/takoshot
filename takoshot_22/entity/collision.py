import math

import pygame

from defines import clamp, STAGE_SKY_HEIGHT


class Stage:

    def __init__(self, surf):
        self.surf = surf
        self.offset = (0, STAGE_SKY_HEIGHT)
        self.rect = pygame.Rect(0, 0, surf.get_width() + self.offset[0], surf.get_height() + self.offset[1])
        self.surf_world_rect = surf.get_rect().move(self.offset[0], self.offset[1])
    
    def create_start_point_list(self):
        list = []
        h = self.surf.get_height() - 1
        
        for x in range(self.surf.get_width()):
            for y in range(h):
            
                # 空白とブロックのペアを探す
                if (not self.surf_block(x, y) and self.surf_block(x, y + 1)):
                    list.append((x + self.offset[0], y + self.offset[1])) # surface to world
                    break
        
        assert len(list) != 0, "サーフェイスに足場がない"
        
        return list

    # x, y がブロックか？
    def is_block(self, x, y):
        if (self.surf_world_rect.collidepoint(x, y)):
            return self.surf_block(*self.world_to_surface(x, y))
        else:
            return False
    
    def get_color(self, x, y):
        if (self.surf_world_rect.collidepoint(x, y)):
            sx, sy = self.world_to_surface(x, y)
            return self.surf.get_at((sx, sy))
        else:
            return (0, 0, 0, 0)
    
    def break_block(self, x, y):
        if (self.surf_world_rect.collidepoint(x, y)):
            sx, sy = self.world_to_surface(x, y)
            self.surf.set_at((sx, sy), (0, 0, 0, 0))
    
    def world_to_surface(self, x, y):
        return x - self.offset[0], y - self.offset[1]

    def surf_block(self, sx, sy):
        return self.surf.get_at((sx, sy)).a != 0

class Collision:

    @classmethod
    def create_line(cls, st_x, st_y, end_x, end_y):
        point_list = []
        dx = end_x - st_x
        dy = end_y - st_y
        n = max(abs(dx), abs(dy))

        # 開始と終点が同じなら終了
        if (n == 0): return [(end_x, end_y)]
        
        for i in range(n + 1):
            point_list.append((int(st_x + dx * i/n), int(st_y + dy * i/n)))
        
        return point_list

    # stage_surface 地形のビットマップ画像
    def __init__(self, stage):
        self.stage = stage

    def clamp_world_x(self, x):
        return clamp(x, self.stage.rect.left, self.stage.rect.right - 1)
    
    def clamp_world_y(self, y):
        return clamp(y, self.stage.rect.top, self.stage.rect.bottom - 1)
    
    def world_rect(self):
        return self.stage.rect
    
    def world_width(self):
        return self.stage.rect.width
    
    def world_height(self):
        return self.stage.rect.height
    
    class Intersect_GroundAndPlayer_Result:
    
        def __init__(self, x, y, is_land):
            self.x = x
            self.y = y
            self.is_land = is_land
        
        def __str__(self):
            return f"x={self.x} y={self.y} is_land={self.is_land}"
    
    def intersect_ground_and_player(self, st_x, st_y, vx, vy):
    
        result = self.collision_x(st_x, st_y, vx)
        x, y = self.collision_y(result.x, result.y, vy)
        
        return Collision.Intersect_GroundAndPlayer_Result(x, y, self.stage.is_block(x, y + 1))
    
    # プレイヤーがワールド外に移動して消滅
    def check_player_lost(self, player_x, player_y):
        return (self.stage.rect.bottom + 50) <= player_y
    
    # 弾がワールド外にあったらTrue
    def check_shell_lost(self, x, y):
        world_rect = self.stage.rect
        return (world_rect.bottom + 100) < y or x < world_rect.left - 100 or world_rect.right + 100 < x
    
    # ワールド内にいるか？
    def is_world_range(self, x, y):
        return self.stage.rect.collidepoint(x, y)    
    
    class CollisionXResult:
        
        def __init__(self, x, y, col_wall, route):
            self.x = x
            self.y = y
            self.collide_wall = col_wall
            self.route = route
        
        def __str__(self):
            return f"x, y={self.x, self.y} collide_wall={self.collide_wall}"
    
    # プレイヤーのx方向の当たり判定を行う
    #
    # return x, y, collide_wall
    def collision_x(self, st_x, st_y, mx):
        
        # 移動なし
        if (mx == 0): return Collision.CollisionXResult(st_x, st_y, False, [])
        
        dir = 1 if (0 < mx) else -1
        
        rect = self.stage.rect
        
        cur_x, cur_y = st_x, st_y
        collide_wall = False
        route = [] # 経路情報
        
        # 一歩ずつｘ座標を移動する
        for x in range(st_x, st_x + mx + dir, dir):
        
            # 左端、右端を超えたら壁扱いにする
            if (x < rect.left or rect.right <= x):
                collide_wall = True
                break
            
            # 1つ先のx座標の地形を調べる
            result = self.search_land_y(x, cur_y)
            
            # 地面を見つけたら移動
            if (result.is_found_land()):
                cur_x = x
                cur_y = result.y
            # 壁なら移動失敗
            elif (result.is_block()):
                collide_wall = True
                break
            else: # air
                cur_x = x
                break
            
            # デバッグとかに使えるかも、経路情報として保存しておく
            route.append([cur_x, cur_y])
        
        return Collision.CollisionXResult(cur_x, cur_y, collide_wall, route)
    
    # プレイヤーのy方向の当たり判定
    def collision_y(self, x, y, my):
        
        found, yy = self.closest_block_y(x, y, my)
        
        if (found):
            dir = 1 if (0 < my) else -1
            ret_y = yy - dir
        else:
            ret_y = y + my
        
        return x, ret_y
    
    class SearchLandYResult:
        Type_Air = "air"
        Type_Block = "block"
        Type_FoundLand = "found_land"
        
        AIR = None
        BLOCK = None
        
        @classmethod
        def found_land(cls, y):
            return cls(cls.Type_FoundLand, y)
        
        def __init__(self, type, y):
            self.type = type
            self.y = y
        
        def __str__(self):
            return f"type={self.type} self.y={self.y}"
        
        def is_found_land(self):
            return self.type == self.Type_FoundLand 
        
        def is_block(self):
            return self.type == self.Type_Block 
        
        def is_air(self):
            return self.type == self.Type_Air
    
    SearchLandYResult.AIR = SearchLandYResult(SearchLandYResult.Type_Air, -1)
    SearchLandYResult.BLOCK = SearchLandYResult(SearchLandYResult.Type_Block, -1)
    
    def search_land_y(self, x, y):
    
        # 現在、ブロックの中にいる
        if (self.stage.is_block(x, y)):
        
            # 現在より上にempty（足場）を探す
            found, yy = self.closest_empty_y(x, y - 1, -2)

            if (found):
                return Collision.SearchLandYResult.found_land(yy) # 足場が見つかった
            else:
                return Collision.SearchLandYResult.BLOCK # ブロックの中にいる

        # ここに処理がきたということは、現在の位置がempty
        # 現在位置より下にブロックを探す
        found, yy = self.closest_block_y(x, y + 1, 2)

        # 足場を見つけた！
        if (found): return Collision.SearchLandYResult.found_land(yy - 1)
        
        # 足場がない、空中にいる
        return Collision.SearchLandYResult.AIR
    
    def closest_empty_y(self, x, y, my):
        return self.closest_block_or_empty_y(x, y, my, False)
    
    def closest_block_y(self, x, y, my):
        return self.closest_block_or_empty_y(x, y, my, True)
    
    def closest_block_or_empty_y(self, x, y, my, block):
    
        vec = 1 if (0 < my) else -1 
        
        end_y = self.clamp_world_y(y + my)
        
        for yy in range(y, end_y + vec, vec):
            
            if (self.stage.is_block(x, yy) == block):
                return True, yy
        
        return False, -1
    
    # キャラクタが上を向いていたらプラス、下を向いていたらマイナス
    def calc_posture_degree(self, x, y, is_right):
        
        # 空中にいるときはまっすぐな姿勢
        if (not self.stage.is_block(x, y + 1)): return 0
        
        total = 0
        length = 26
        vec = 1 if is_right else -1
        count = 0
        cur_y = y
        
        # 自分の足元を数箇所調べて、平均の傾きを計算する
        for ofs_x in range(length):
            
            ret = self.search_land_y(x + ofs_x * vec, cur_y)
            
            if (ret.is_found_land()):
                total += (ret.y - cur_y) * 0.8
                count += 1
                cur_y = y
            elif (ret.is_block()): # 壁にぶつかったらとりあえず終了させとく
                total += -6 # ほぼ真上を見上げる姿勢
                count += 1
                break
            elif (ret.is_air()): # 地面がなかったら終了する
                total += 6
                count += 1
                break
        
        if (count == 0): return 0
        
        # 平均値の算出
        return -(total / count) * 15
    
    # 地面を破壊する（円形）
    #
    # breaked_list 破壊されたドット(x, y, color)のリスト
    def break_block_in_circle(self, x, y, radius, breaked_list = []):
        circle_xy_list = []
        self.create_circle(x, y, radius, circle_xy_list)
        
        for x, y in circle_xy_list:
            
            if (self.stage.is_block(x, y)):
                
                color = self.stage.get_color(x, y)
                self.stage.break_block(x, y)
                breaked_list.append((x, y, color))

    def create_circle(self, center_x, center_y, radius, out_list):
        
        rq = radius * radius
        
        for ofs_y in range(-radius, radius + 1):
            ofs_x = math.sqrt(rq - ofs_y * ofs_y)
            left = int(center_x - ofs_x)
            right = int(center_x + ofs_x)
            y = center_y + ofs_y
            
            for x in range(left, right + 1):
                out_list.append((x, y))
    
    def intersect_ground_and_line_segment(self, st_x, st_y, vx, vy):
        
        end_x, end_y = st_x + vx, st_y + vy
        
        point_list = self.create_line(st_x, st_y, end_x, end_y)
        hit, cur_x, cur_y = False, st_x, st_y
        
        # 一歩ずつ移動する
        for x, y in point_list:
            # 障害物があったら移動失敗！
            if (self.stage.is_block(x, y)):
                hit = True
                break
            
            # 移動する
            cur_x, cur_y = x, y
        
        return hit, cur_x, cur_y
    
    def intersect_circle_and_players(self, x, y, radius, player_list):
        list = []
        rr = radius * radius
        
        for player in player_list:
            dx = abs(player.x - x)
            dy = abs(player.y - y)
            dd = dx * dx + dy * dy
            
            if (dd <= rr):
                list.append({'player':player, 'dist':math.sqrt(dd)})
        
        return list
