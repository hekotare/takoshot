import math

import globals as g
from core.input_sys import KeyCodes
from entity.world import World
from geometry import Geometry


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
        # 地形を破壊する
        if (input_sys.is_push(KeyCodes.MOUSE_RIGHT)):
            self.world.collision.break_block_in_circle(*input_sys.mouse_pos, 20)
    
    def render(self):
        g.graphics.fill((128, 128, 255))
        self.world.render()
        self.draw_posture_line()
    
    def draw_posture_line(self):
        player_x, player_y = self.user_player.x, self.user_player.y

        posture_degree = self.world.collision.calc_posture_degree(player_x, player_y, True)
        rad = math.radians(posture_degree)
        
        x0, y0 = Geometry.rotate(-40, 0, rad)
        x1, y1 = Geometry.rotate(40, 0, rad)
        
        p0 = (x0 + player_x, y0 + player_y)
        p1 = (x1 + player_x, y1 + player_y)
        
        g.graphics.line((0, 255, 0), p0, p1)

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame())