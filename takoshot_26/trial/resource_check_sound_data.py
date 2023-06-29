import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import play_se


# ターミナルから
# python -m trial.resource_check_sound_data を入力し、実行
class Scene_ResCheck_SoundData(Scene):

    def __init__(self):
        super().__init__(g.systems)
    
    def prepare(self):
        self.cursor = 0
        self.sound_name_list = g.systems.res_sys.sound.get_sound_name_list()
    
    def dispose(self):
        pass
    
    def update(self):
        input = g.systems.input_sys

        # サウンドの切り替え
        if ( input.is_push(KeyCodes.UP)):
            self.cursor = (self.cursor - 1) % len(self.sound_name_list)
        elif ( input.is_push(KeyCodes.DOWN)):
            self.cursor = (self.cursor + 1) % len(self.sound_name_list)
        
        # サウンドの再生
        if ( input.is_push(KeyCodes.Z)):
            play_se(g.systems, self.sound_name_list[self.cursor])
    
    def render(self):
    
        # 背景を白に
        g.graphics.fill((255, 255, 255))
        # サウンドの名前
        g.graphics.text((20, 20), self.sound_name_list[self.cursor], (64, 64, 64))


if __name__ == '__main__':
    main.main(Scene_ResCheck_SoundData)
