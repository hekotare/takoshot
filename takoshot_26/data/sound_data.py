import pygame

from defines import SOUND_DATA_LIST


class SoundDataManager:

    def load(self):
    
        sound_name_list = []
        map = {}
        
        for sound_data in SOUND_DATA_LIST:
            sound_name = sound_data[0]
            file_path = sound_data[1]
            
            sound = pygame.mixer.Sound("res/sound/" + file_path)
            
            sound_name_list.append(sound_name)
            map[sound_name] = { 'sound':sound, 'path':file_path }
        
        self._sound_name_list = sound_name_list
        self._map = map
    
    def get_sound(self, sound_name):
        return self._map[sound_name]['sound']
    
    def get_filepath(self, sound_name):
        return self._map[sound_name]['path']
    
    def get_sound_name_list(self):
        return self._sound_name_list
