import math

import pygame

import globals as g
from core.input_sys import KeyCodes
from core.scene import Scene, Scene_Container
from defines import (BattleInitInfo, ChrType, SceneId, StageId, play_bgm,
                     stop_bgm)
from scene.maingame import Scene_MainGame

# python -m scene.menu を入力し実行

last_battle_info = None

rect_list = [
    [ 20,  20, 400,  80], # player_1
    [ 20, 120, 400,  80], # player_2
    [440,  20, 180, 240], # stage select
    [ 20, 380, 200,  60], # button
]

# array から pygame.Rect に変換する
#rect_list = [pygame.Rect(1, 1, 2, 2) for rect in rect_list]
rect_list = [pygame.Rect(rect[0], rect[1], rect[2], rect[3]) for rect in rect_list]

class Scene_GameRoot(Scene_Container):

    def __init__(self):
        super().__init__(g.systems, SceneId.GAME_ROOT)
    
    def prepare(self):
        #self.add_child(Scene_Title())

        # バトル設定画面を接続
        self.add_child(Scene_PreparingForBattle())
    
    def on_end_child_scene(self, child_scene):
    
        if (child_scene.id is SceneId.PREPARING_FOR_BATTLE):
            self.add_child( Scene_MainGame(child_scene.result_param))
        
        elif (child_scene.id is SceneId.MAINGAME):
            self.add_child( Scene_PreparingForBattle())
        
        else:
            assert False, f"child_scene.id={child_scene.id}"


# バトル設定画面
class Scene_PreparingForBattle(Scene_Container):

    def __init__(self):
        super().__init__(g.systems, SceneId.PREPARING_FOR_BATTLE)
    
    def prepare(self):
    
        menu_cntr = MenuItem_Container()
        
        menu_cntr.add_item(MenuItem(ChrType.ORANGE)) # player 1
        menu_cntr.add_item(MenuItem(ChrType.GREEN)) # player 2
        menu_cntr.add_item(MenuItem(StageId.IWAYAMA)) # stage
        menu_cntr.add_item(MenuItem()) # Start Button
        
        self.menu_cntr = menu_cntr
        self.menu_cntr.cursor = 3

        # 過去のバトル設定を読み込む
        if last_battle_info is not None:
            self.menu_cntr.items[0].data = last_battle_info.player_0
            self.menu_cntr.items[1].data = last_battle_info.player_1
            self.menu_cntr.items[2].data = last_battle_info.stage_id
        
        play_bgm(g.systems, "menu")
    
    def dispose(self):
        stop_bgm(g.systems)
    
    def on_update(self):

        global last_battle_info
        input_sys = g.systems.input_sys

        # 決定ボタンを押した
        if (input_sys.is_push(KeyCodes.Z)):
            cursor = self.menu_cntr.cursor
            selected_data = self.menu_cntr.items[cursor].data

            if (0 <= cursor <= 1):
                self.add_child(Scene_CharacterSelect(cursor, selected_data))
            elif (cursor == 2):
                self.add_child(Scene_StageSelect(cursor, selected_data))
            elif (cursor == 3):
                btlinfo_info = self.create_battleInit_info()
                last_battle_info = self.create_battleInit_info()
                self.end_scene(Scene.Result.OK, btlinfo_info)
                return

        if (input_sys.is_push(KeyCodes.UP)):
            self.menu_cntr.prev()
        elif (input_sys.is_push(KeyCodes.DOWN)):
            self.menu_cntr.next()
    
    def on_render(self):
        
        rect = rect_list[self.menu_cntr.cursor]
        draw_cursor(rect)
        
        draw_player(rect_list[0], self.menu_cntr.items[0].data, "PLAYER 1")
        draw_player(rect_list[1], self.menu_cntr.items[1].data, "PLAYER 2")
        draw_stage_select(rect_list[2], self.menu_cntr.items[2].data)
        draw_start_button(rect_list[3])
    
    def on_end_child_scene(self, child_scene):

        # 子シーンのidにカーソルのインデックスを使用している
        # 0, 1 ならキャラ選択画面, 2 ならステージ選択画面
        cursor = child_scene.id

        if (0 <= cursor <= 2 and
            child_scene.has_result_ok()):
            self.menu_cntr.items[cursor].data = child_scene.result_param

    def create_battleInit_info(self):
    
        info = BattleInitInfo()
        
        info.player_0 = self.menu_cntr.items[0].data
        info.player_1 = self.menu_cntr.items[1].data
        info.stage_id = self.menu_cntr.items[2].data
        
        return info

class Scene_CharacterSelect(Scene):

    def __init__(self, scene_id, selected_data):
        
        super().__init__(g.systems, scene_id)

        self.type_list = g.systems.res_sys.chrdata.type_list()
        self.character_num = len(self.type_list)
        self.cursor = self.type_list.index(selected_data)

    def update(self):
        
        input_sys = g.systems.input_sys
        m = 0
        
        if (input_sys.is_push(KeyCodes.Z)):
            # キャラの名前を返す
            self.end_scene(Scene.Result.OK, self.type_list[self.cursor])
            return
        
        if (input_sys.is_push(KeyCodes.X)):
            self.end_scene(Scene.Result.CANCEL)
            return
        
        if (input_sys.is_keydown(KeyCodes.UP, repeat_frame=10)):
            m = -4
        elif (input_sys.is_keydown(KeyCodes.DOWN, repeat_frame=10)):
            m = 4
        elif (input_sys.is_keydown(KeyCodes.LEFT, repeat_frame=10)):
            m = -1
        elif (input_sys.is_keydown(KeyCodes.RIGHT, repeat_frame=10)):
            m = 1
        
        self.cursor = (self.cursor + m) % self.character_num
        
        assert self.character_num % 4 == 0, "キャラクタの数が4の倍数じゃなくなったら修正必要"
            
    
    def render(self):
        
        rect = pygame.Rect(100, 100, 400, 300)
        g.graphics.rectangle((rect.x, rect.y, rect.width, rect.height), fill=BackGround, outline=OutLine, width=Width)
        
        x, y = self.index_to_xy(self.cursor)
        rect2 = pygame.Rect(rect.x + 20 + x * 70, rect.y + 20 + y * 70, 64, 64)
        draw_cursor(rect2)
        
        for index in range(self.character_num):
            bmp_name = g.systems.res_sys.chrdata.bmp_name(self.type_list[index])
            img = g.systems.res_sys.bitmap.get_bitmap(bmp_name, 0)
            x, y = self.index_to_xy(index)
            
            xx = rect.x + 20 + x * 70
            yy = rect.y + 20 + y * 70
            g.graphics.blit(img, (xx, yy))
            g.graphics.rectangle((xx, yy, 64, 64), outline=OutLine, width=2)
    
    def index_to_xy(self, index):
        return (index % 4), int(index / 4)


class Scene_StageSelect(Scene):

    COLUMNS = 4

    def __init__(self, scene_id, selected_data):
        super().__init__(g.systems, scene_id)
        
        self.id_list = g.systems.res_sys.stage.id_list()
        self.cursor = self.id_list.index(selected_data)
    
    def update(self):
        # カーソルの移動
        input_sys = g.systems.input_sys
        x, y = 0, 0
        stage_num = len(self.id_list)
        rows = math.ceil(stage_num / self.COLUMNS)

        if (input_sys.is_push(KeyCodes.Z)):
            self.end_scene(Scene.Result.OK, self.id_list[self.cursor])
            return
        
        if (input_sys.is_push(KeyCodes.X)):
            self.end_scene(Scene.Result.CANCEL)
            return

        if (input_sys.is_keydown(KeyCodes.UP, repeat_frame=10)):
            y = -1
        elif (input_sys.is_keydown(KeyCodes.DOWN, repeat_frame=10)):
            y = 1
        elif (input_sys.is_keydown(KeyCodes.LEFT, repeat_frame=10)):
            x = -1
        elif (input_sys.is_keydown(KeyCodes.RIGHT, repeat_frame=10)):
            x = 1
        
        if (y):
            self.cursor = (self.cursor + (y * self.COLUMNS)) % (self.COLUMNS * rows)        
            self.cursor = min(self.cursor, stage_num - 1)
        elif (x):
            self.cursor = (self.cursor + x) % stage_num
    
    def render(self):
        g.graphics.rectangle((45, 60, 550, 250), fill=BackGround, outline=OutLine, width=Width)
        g.graphics.rectangle((45, 60, 550, 40), fill=OutLine)

        for i, stage_id in enumerate(self.id_list):
            x, y = self.index_to_xy(i)
            surf = g.systems.res_sys.stage.thumbnail(stage_id)
            g.graphics.blit(surf, (45 + 20 + x * 130, 100 + 20 + y * 90))
        
        x, y = self.index_to_xy(self.cursor)
        g.graphics.rectangle((45 + 20 + x * 130, 100 + 20 + y * 90, 120, 90), outline=(255, 0, 0), width=Width)
    
    def index_to_xy(self, index):
        return index % self.COLUMNS, int(index / self.COLUMNS)

class MenuItem:
    def __init__(self, data = None):
        self.data = data


class MenuItem_Container:

    def __init__(self):
        super().__init__()
        
        self._cursor = 0
        self._item_num = 0
        self._items = []
    
    def prev(self):
        self._change_cursor(self._cursor - 1)

    def next(self):
        self._change_cursor(self._cursor + 1)
    
    def _change_cursor(self, new_pos):
        # loop
        self._cursor = new_pos % self._item_num
    
    def add_item(self, item):
        self._items.append(item)
        self._item_num = len(self._items)
    
    @property
    def cursor(self):
        return self._cursor
    
    @cursor.setter
    def cursor(self, pos):
        self._change_cursor(pos)
    
    @property
    def selected_item(self):
        return self._items[self._cursor]
    
    @property
    def items(self):
        return self._items


BackGround  = (32, 32, 32)
OutLine     = (128, 128, 128)
Width       = 4
CursorFill  = (160, 160, 160)

def draw_player(rect, chr_type, label):
    
    g.graphics.rectangle((rect.x, rect.y, rect.width, rect.height), outline=OutLine, width=Width)
    g.graphics.text((rect.x + 20, rect.y + 20), label, (255, 255, 255))

    bmp_name = g.systems.res_sys.chrdata.bmp_name(chr_type)
    img = g.systems.res_sys.bitmap.get_bitmap(bmp_name, 0)
    
    g.graphics.blit(img, (rect.x + 320, rect.y + 10))

def draw_stage_select(rect, stage_id):
    g.graphics.rectangle((rect.x, rect.y, rect.width, rect.height), outline=OutLine, width=Width)
    g.graphics.rectangle((rect.x, rect.y, rect.width, 40), fill=OutLine)
    
    g.graphics.text((rect.x + rect.width * 0.5, rect.y + 8), "STAGE SELECT", (255, 255, 255), textalign="center")
    
    img = g.systems.res_sys.stage.thumbnail(stage_id)
    g.graphics.blit(img, (rect.x + 30, rect.y + 80))

def draw_start_button(rect):
    g.graphics.rectangle((rect.x, rect.y, rect.width, rect.height), outline=OutLine, width=Width)
    g.graphics.text((rect.x + rect.width * 0.5, rect.y + 16), "START", (255, 255, 255), textalign="center")

def draw_cursor(rect):
    g.graphics.rectangle((rect.x, rect.y, rect.width, rect.height), fill=CursorFill, width=Width)

if __name__ == '__main__':
    import main
    main.main(Scene_GameRoot, window_width=1200)
