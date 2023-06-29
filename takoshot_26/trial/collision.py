import math

import pygame

import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from entity.collision import Collision, Stage

CELL_SIZE = 24

COLOR_BLOCK  = pygame.Color(255, 255, 255)
COLOR_EMPTY = (0, 0, 0, 0)

COLOR_MOVED_CHR = (128, 255, 128)
COLOR_MOVE_VECTOR = (255, 128, 128)

# テスト用のステージを作成
def create_stage_surface():
    # 透過ビットマップの作成
    surface = pygame.Surface((24, 18), pygame.SRCALPHA)
    surface.fill(color = COLOR_EMPTY)
    
    # 小さな山
    surface.set_at((9,  9), COLOR_BLOCK)
    surface.set_at((9, 10), COLOR_BLOCK)
    
    # 壁
    surface.set_at((10,  6), COLOR_BLOCK)
    surface.set_at((10,  7), COLOR_BLOCK)
    surface.set_at((10,  8), COLOR_BLOCK)
    surface.set_at((10,  9), COLOR_BLOCK)
    surface.set_at((10, 10), COLOR_BLOCK)
    
    # 隙間あり１
    surface.set_at((11,  6), COLOR_BLOCK)
    surface.set_at((11,  8), COLOR_BLOCK)
    surface.set_at((11, 10), COLOR_BLOCK)
    # 隙間あり２
    surface.set_at((12,  6), COLOR_BLOCK)
    surface.set_at((12,  9), COLOR_BLOCK)
    surface.set_at((12, 11), COLOR_BLOCK)
    
    # 隅っこ
    for y in [0, int(surface.get_height() * 0.5), surface.get_height() - 1]:
        for x in [0, int(surface.get_width() * 0.5), surface.get_width() - 1]:
            surface.set_at((x,  y), COLOR_BLOCK)

    return surface

def create_chr_surf():
    surf = pygame.image.load('res/image/chr01.png').convert_alpha()
    return pygame.transform.scale(surf, (CELL_SIZE, CELL_SIZE))

#
# Collisionクラスの
# ブロックとの当たり判定をおためし
#
# python -m trial.collision を入力し実行
class Scene_TryCollision(Scene):

    Test_SearchLandY = 0
    TEST_COL_X = 1
    Test_INTERSECT_G_A_P = 2
    Test_Num = 3
    
    def __init__(self):
        super().__init__(g.systems)

    def prepare(self):
        
        self.mode = self.Test_SearchLandY
        self.mapedit = False
        self.st_x = 10
        self.st_y =  9
        self.end_x = 10
        self.end_y =  9
        self.chr_surf = create_chr_surf()
        
        self.stage_surf = create_stage_surface()
        self.collision = Collision(Stage(self.stage_surf))
    
    def update(self):
        
        input_sys = g.systems.input_sys
        
        if (input_sys.is_push(KeyCodes.KEY_1)):
            self.mode = (self.mode + 1) % self.Test_Num
        
        mouse_pos = self.world_to_cell(*input_sys.mouse_pos)
        
        if (input_sys.is_push(KeyCodes.KEY_2)):
            self.mapedit = not self.mapedit # toggle
        else:
            
            # マップ編集モード
            if (self.mapedit):
                if input_sys.is_keydown(KeyCodes.MOUSE_LEFT):
                    self.stage_surf.set_at(mouse_pos, COLOR_BLOCK)
                elif input_sys.is_keydown(KeyCodes.MOUSE_RIGHT):
                    self.stage_surf.set_at(mouse_pos, COLOR_EMPTY)
            
            else:
                # move player
                if (input_sys.is_push(KeyCodes.MOUSE_LEFT)):
                    self.st_x, self.st_y = mouse_pos
                elif (input_sys.is_push(KeyCodes.MOUSE_RIGHT)):
                    self.end_x, self.end_y = self.world_to_cell(*input_sys.mouse_pos)
        
        if (self.mode == self.Test_SearchLandY):
            self.result = self.collision.search_land_y(self.st_x, self.st_y)
        elif (self.mode == self.TEST_COL_X):
            self.result = self.collision.collision_x(self.st_x, self.st_y, self.end_x - self.st_x)
        elif (self.mode == self.Test_INTERSECT_G_A_P):
            self.result = self.collision.intersect_ground_and_player(self.st_x, self.st_y, 
                                                            self.end_x - self.st_x, self.end_y - self.st_y)

    def draw_cell(self, x, y, fill, outline):
        g.graphics.rectangle((x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),fill=fill, outline=outline, width=2)
    
    def draw_grid(self):
        for x in range(0, math.ceil(g.WINDOW_RECT.width / CELL_SIZE)):
            g.graphics.line((255, 255, 255), (x * CELL_SIZE, 0), (x * CELL_SIZE, g.WINDOW_RECT.height))
        
        for y in range(0, math.ceil(g.WINDOW_RECT.height / CELL_SIZE)):
            g.graphics.line((255, 255, 255), (0, y * CELL_SIZE), (g.WINDOW_RECT.width, y * CELL_SIZE))
    
    def draw_world(self):
        rect = self.collision.stage.rect.copy()
        rect.left, rect.top = self.cell_to_world(rect.left, rect.top)
        rect.right, rect.bottom = self.cell_to_world(rect.right, rect.bottom)
        
        # draw block or empty
        for y in range(self.collision.world_height()):
            for x in range(self.collision.world_width()):
                fill = self.collision.stage.get_color(x, y)
                self.draw_cell(x, y, fill, (64, 64, 64))
    
    def draw_chr(self, cx, cy):
        g.graphics.blit(self.chr_surf, self.cell_to_world(cx, cy))
    
    def world_to_cell(self, x, y):
        return (int(x / CELL_SIZE), int(y / CELL_SIZE))
    
    def cell_to_world(self, cx, cy):
        return (cx * CELL_SIZE, cy * CELL_SIZE)
    
    def cell_to_world_center(self, cx, cy):
        return ((cx + 0.5) * CELL_SIZE, (cy + 0.5) * CELL_SIZE)

    def render(self):
        
        # 共通部分
        self.draw_grid()
        self.draw_world()
        self.draw_chr(self.st_x, self.st_y)

        debug_sys = g.systems.debug_sys
        debug_sys.text("- controls -", (255, 255, 255))
        debug_sys.text("KEY_1 : MODE CHANGE", (255, 255, 255))
        debug_sys.text("KEY_2: MAP EDIT MODE", (255, 255, 255))

        if self.mapedit:
            debug_sys.text("MOUSE_LEFT: put Block", (255, 255, 255))
            debug_sys.text("MOUSE_RIGHT: remove Block", (255, 255, 255))
        else:
            debug_sys.text("MOUSE_LEFT: start pos", (255, 255, 255))
            debug_sys.text("MOUSE_RIGHT: end pos", (255, 255, 255))
        
        debug_sys.text("", (255, 255, 255))

        # モードによって描画
        if (self.mode == self.Test_SearchLandY):
            self.render_1()
        elif (self.mode == self.TEST_COL_X):
            self.render_2()
        elif (self.mode == self.Test_INTERSECT_G_A_P):
            self.render_3()
        
        if (self.mapedit):
            g.graphics.text((20, 20), "- MAP EDIT MODE -", (255, 255, 255), background=(0, 0, 0), font=g.font_i20)
    
    def render_1(self):
    
        g.systems.debug_sys.text(f"TEST search_land_y", (255, 255, 255))
        g.systems.debug_sys.text(f"result:{self.result}", (255, 255, 255))
        
        if (self.result.type == Collision.SearchLandYResult.Type_FoundLand):
            g.graphics.circle((self.cell_to_world_center(self.st_x, self.result.y)),
                        CELL_SIZE * 0.25, fill=COLOR_MOVED_CHR, outline=(255, 255, 255))
    
    def render_2(self):
    
        g.systems.debug_sys.text(f"TEST collision_x", (255, 255, 255))
        g.systems.debug_sys.text(f"result:{self.result}", (255, 255, 255))

        # 移動ベクトル
        g.graphics.line(COLOR_MOVE_VECTOR, self.cell_to_world_center(self.st_x, self.st_y), self.cell_to_world_center(self.end_x, self.st_y))
        
        # 移動後座標
        g.graphics.circle((self.cell_to_world_center(self.result.x, self.result.y)),
            CELL_SIZE * 0.25, fill=COLOR_MOVED_CHR, outline=(255, 255, 255))
        
        # 移動経路
        for x, y in self.result.route:
            g.graphics.circle((self.cell_to_world_center(x, y)),
                CELL_SIZE * 0.1, fill=(128, 255, 128), outline=(255, 255, 255))
    
    def render_3(self):
    
        g.systems.debug_sys.text(f"TEST intersect_ground_and_player", (255, 255, 255))
        g.systems.debug_sys.text(f"result:{self.result}", (255, 255, 255))

        # 移動ベクトル
        g.graphics.line(COLOR_MOVE_VECTOR, self.cell_to_world_center(self.st_x, self.st_y), self.cell_to_world_center(self.end_x, self.end_y))
        
        # 移動後座標
        g.graphics.circle((self.cell_to_world_center(self.result.x, self.result.y)),
            CELL_SIZE * 0.25, fill=COLOR_MOVED_CHR, outline=(255, 255, 255))

if __name__ == '__main__':
    main.main(Scene_TryCollision, window_width = 1200)
