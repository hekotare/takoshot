import math

from defines import clamp


class Stage:

    def __init__(self, surf):
        import pygame
        self.surf = surf
        self.rect = pygame.Rect(0, 0, surf.get_width(), surf.get_height())
    
    # x, y がブロックか？
    def is_block(self, x, y):

        if (self.is_range(x, y)):
            return self.surf.get_at((x, y)).a != 0
        else:
            return False
    
    def get_color(self, x, y):
        if (self.is_range(x, y)):
            return self.surf.get_at((x, y))
        else:
            return (0, 0, 0, 0)
    
    def is_range(self, x, y):
        return self.rect.collidepoint(x, y)

class Collision:

    # stage_surface 地形のビットマップ画像
    def __init__(self, stage):
        self.stage = stage

    def clamp_world_x(self, x):
        return clamp(x, self.stage.rect.left, self.stage.rect.right - 1)
    
    def clamp_world_y(self, y):
        return clamp(y, self.stage.rect.top, self.stage.rect.bottom - 1)
    
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
