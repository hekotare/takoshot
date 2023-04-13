import globals as g
from entity.world import World


# python -m trial.maingame を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/maingame.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_MainGame:

    def prepare(self):
        self.world = World()
        self.world.add_player(140, 140)
    
    def update(self):
        self.world.update()
    
    def render(self):
        g.graphics.fill((128, 128, 255))
        self.world.render()

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame())