import pygame

import graphics
from defines import STAGE_DATA_LIST, clamp


class BitmapDataManager:

    # img_srcからスプライトを切り取る
    @classmethod
    def cut_images(cls, img_src, x, y, w, h, num_steps_x, num_steps_y):
    
        list = []
        
        for iy in range(num_steps_y):
            xx = x
            for ix in range(num_steps_x):
                surface = pygame.Surface((w, h), flags=pygame.SRCALPHA)
                surface.blit(img_src, (0, 0), (xx, y, w, h))
                list.append(surface.convert_alpha())
                
                xx += w
            
            y += h
        
        return list
    
    def __init__(self):
        self.map = {}
    
    def load(self):
        
        self.map = {}
        
        self.register('stage', 
                      [pygame.image.load(f'res/image/{data}').convert_alpha() for data in STAGE_DATA_LIST])
        
        img_src = pygame.image.load('res/image/icon.png').convert_alpha()
        self.register('item_icon',
                    BitmapDataManager.cut_images(img_src, x = 0, y = 0, w = 32, h = 32, num_steps_x = 6, num_steps_y = 1))
        
        img_src = pygame.image.load('res/image/shell001.png').convert_alpha()
        self.register('shell001',
            [graphics.rotate(img_src, degree) for degree in range(0, 360, 60)])
        
        img_src = pygame.image.load('res/image/shell_warp.gif').convert_alpha()
        
        self.register('shell_warp',
            BitmapDataManager.cut_images(img_src, x = 0, y = 0, w = 44, h = 44, num_steps_x = 2, num_steps_y = 1))
        
        img_src = pygame.image.load('res/image/shell002.png').convert_alpha()
        
        self.register('shell002',
            BitmapDataManager.cut_images(img_src, x = 0, y = 0, w = 16, h = 16, num_steps_x = 3, num_steps_y = 1))
        
        img_src = pygame.image.load('res/image/shell003.png').convert_alpha()
        self.register('shell003',[img_src])
        
        img_src = pygame.image.load('res/image/character.png').convert_alpha()

        chr_bmp_list = BitmapDataManager.cut_images(img_src, x = 0, y = 0, w = 64, h = 64, num_steps_x = 3, num_steps_y = 3)
        chr_flip_bmp_list = [graphics.flip(img) for img in chr_bmp_list]
        self.register('chr001', chr_bmp_list + chr_flip_bmp_list)
        
        # chr002～chr008を追加する
        # (とりあえず、仮データとしてchr001の色違いを作っておく)
        skin = (255, 127,  39)
        line = (0, 0, 0)
        
        replace_data_list = [
            [[skin, (201, 255,  38)]], # chr002の色
            [[skin, ( 38, 190, 255)]], # chr003の色
            [[skin, (254,  39, 254)]], # chr004の色
            [[skin, (132, 105,  60)]], # chr005の色
            [[skin, (106,  60, 132)]], # chr006の色
            [[skin, ( 32,  32,  32)], [line, (214, 214, 214)]], # chr007の色
            [[skin, (255, 255, 255)]]  # chr008の色
        ]
        
        src_bitmap_list = self.get_bitmap_list('chr001')
        for i, color_list in enumerate(replace_data_list, start=2):
            self.register(f'chr00{i}',
            [ graphics.replace(img, color_list) 
                        for img in src_bitmap_list])
    
    def register(self, bitmap_name, items):
        assert self.map.get(bitmap_name) == None, f"すでに登録済みです bitmap_name={bitmap_name}"
        
        self.map[bitmap_name] = items
        return items
    
    def get_bitmap_list(self, bitmap_name):
        
        return self.map[bitmap_name]
    
    def get_bitmap(self, bitmap_name, idx):
        bitmaps = self.get_bitmap_list(bitmap_name)
        
        # 最大インデックスを超えないように丸める, ほかにもidxのループとか作っても良いかも
        i = int(clamp(idx, 0, len(bitmaps) - 1))
        
        return bitmaps[i]
    
    def get_bitmap_name_list(self):
        return list(self.map.keys())

