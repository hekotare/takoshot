import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene


# ターミナルから
# python -m trial.resource_check_bitmap_data を入力し、実行
class Scene_ResCheck_BitmapData(Scene):

    def prepare(self):
        self.cursor = 0
        self.bitmap_index = 0
        self.bitmap_name_list = g.systems.res_sys.bitmap.get_bitmap_name_list()
        self.bitmap_index_num = len(self.get_selected_bitmaps())
    
    def dispose(self):
        pass
    
    def update(self):
    
        bitmap_name_list = self.bitmap_name_list
        input = g.systems.input_sys

        # ビットマップリストの切り替え
        repeat_frame = 20
        if ( input.is_keydown(KeyCodes.W, repeat_frame)):
            self.cursor = (self.cursor + 1) % len(bitmap_name_list)
            self.bitmap_index = 0
            self.bitmap_index_num = len(self.get_selected_bitmaps())
        elif ( input.is_keydown(KeyCodes.S, repeat_frame)):
            self.cursor = (self.cursor - 1) % len(bitmap_name_list)
            self.bitmap_index = 0
            self.bitmap_index_num = len(self.get_selected_bitmaps())
        # インデックスの変更
        elif ( input.is_keydown(KeyCodes.A, repeat_frame)):
            self.bitmap_index = (self.bitmap_index - 1) % self.bitmap_index_num
        elif ( input.is_keydown(KeyCodes.D, repeat_frame)):
            self.bitmap_index = (self.bitmap_index + 1) % self.bitmap_index_num
    
    def get_selected_bitmaps(self):
        
        bitmap_name = self.bitmap_name_list[self.cursor]
        return g.systems.res_sys.bitmap.get_bitmap_list(bitmap_name)
    
    def render(self):
    
        g.graphics.fill((214, 160, 90))
        
        bitmap_name = self.bitmap_name_list[self.cursor]
        bitmaps = g.systems.res_sys.bitmap.get_bitmap_list(bitmap_name)
        
        white_color = (255, 255, 255)

        # ビットマップリストの名前
        g.systems.debug_sys.text(f"bitmap_name: {bitmap_name}", white_color)
        # ビットマップ番号
        g.systems.debug_sys.text(f"bitmap_index: - {self.bitmap_index} / {len(bitmaps) - 1} -", white_color)
        
        # ビットマップそのものを描画
        img = bitmaps[self.bitmap_index]
        g.graphics.blit(img, (100, 100))

        g.graphics.line((32, 32, 32), ( 80, 100), (100 + img.get_width() + 20, 100))
        g.graphics.line((32, 32, 32), (100,  80), (100, 100 + img.get_height() + 20))

        g.systems.debug_sys.text("- controls -", white_color)
        g.systems.debug_sys.text("W, S KEY: change bitmap_name", white_color)
        g.systems.debug_sys.text("A, D KEY: change bitmap_index", white_color)

if __name__ == '__main__':
    main.main(Scene_ResCheck_BitmapData(), window_width = 1200)
