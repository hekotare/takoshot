import pygame

from defines import STAGE_DATA_LIST


class StageDataManager:

    def load(self, bmpdata_mgr):
    
        self.bmpdata_mgr = bmpdata_mgr
        self.id_to_data_map = {}
        
        # ステージデータの作成
        for bmp_idx, d in enumerate(STAGE_DATA_LIST):
            id, _, bgm_name = d
            self.id_to_data_map[id] = (id, bmp_idx, bgm_name)

        # ステージ画像の読み込み
        bitmap_list = []
        
        for bmp_idx, d in enumerate(STAGE_DATA_LIST):
            bitmap_list.append(pygame.image.load(f'res/image/{d[1]}').convert_alpha())
        
        bmpdata_mgr.register('stage', bitmap_list)

        # ステージのサムネを作成
        thumbnail_list = []

        for img in bitmap_list:
            img = pygame.transform.scale(img, (120, 90))
            new_img = pygame.Surface((120, 90))
            new_img.fill((64, 64, 128))
            new_img.blit(img, (0, 0))
            thumbnail_list.append(new_img)
        
        bmpdata_mgr.register('stage_thumbnail', thumbnail_list)
    
    def bitmap(self, id):
        bmp_index = self.id_to_data_map[id][1]
        return self.bmpdata_mgr.get_bitmap('stage', bmp_index)

    def thumbnail(self, id):
        bmp_index = self.id_to_data_map[id][1]
        return self.bmpdata_mgr.get_bitmap('stage_thumbnail', bmp_index)
    
    def bgm_name(self, id):
        return self.id_to_data_map[id][2]
    
    def id_list(self):
        return list(self.id_to_data_map.keys())
    