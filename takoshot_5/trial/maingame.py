import globals as g
from core.input_sys import KeyCodes
from entity.world import World


# python -m trial.maingame を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/maingame.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_MainGame:

    def prepare(self):
        self.world = World()
        self.user_player = self.world.add_player(140, 140)
    
    def update(self):
        self.world.update()

        input_sys = g.systems.input_sys
        command = self.user_player.command
        
        # プレイヤーを操作する
        if (input_sys.is_keydown(KeyCodes.A)):
            command.move_left()
        if (input_sys.is_keydown(KeyCodes.D)):
            command.move_right()
        
        # debug プレイヤーをワープさせる
        if (input_sys.is_push(KeyCodes.MOUSE_LEFT)):
            self.user_player.x, self.user_player.y = input_sys.mouse_pos
    
    def render(self):
        g.graphics.fill((128, 128, 255))
        self.world.render()

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame())