# 音量調整いいかげんだけどとりあえずこれでいいかな
# ほんとーは音量を変更したときに再生中の音楽や効果音の音量も変更しなきゃダメかも
class SoundSys:

    def init(self):
        self.bgm = None
        self.master_volume = 1.0
        self._bgm_volume = 0.1
        self._se_volume = 0.1
    
    def play_bgm(self, sound):
    
        self.stop_bgm()
        
        sound.set_volume(self.master_volume * self._bgm_volume)
        self.bgm = { 'sound': sound, 'channel': sound.play(loops = -1) }
    
    def stop_bgm(self):
    
        if (self.bgm != None):
            self.bgm['sound'].stop()
            self.bgm = None
    
    def play_once_se(self, sound):
        sound.set_volume(self.master_volume * self._se_volume)
        sound.play()
