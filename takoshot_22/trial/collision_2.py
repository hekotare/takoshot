import math

import globals as g
from core.input_sys import KeyCodes
from core.scene import Scene
from game import Game
from geometry import Geometry
from defines import StageId
import random

# ステージの地形破壊、プレイヤーの傾きや落下をテスト
#
# python -m trial.collision_2 を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/collision_2.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_TryCollision2(Scene):

    RADIUS = 20

    def prepare(self):
        self.game = Game()
        self.game.create_world(StageId.MOKUZAI)
        
        stage = self.game.world.stage
        p_list = stage.create_start_point_list()
        x, y = random.choice(p_list)
        self.user_player = self.game.world.add_player(x, y)
        self.game.camera.x = x
        self.game.camera.y = y
        self.game.cameraman.set_target_entity(self.user_player)

        # デバッグ：プレイヤーの初期座標リストをサーフェイスに直接書き込みして、見えるようにする
        for xy in p_list:
            stage.surf.set_at(stage.world_to_surface(*xy), (0, 255, 0))
    
    def update(self):
        self.game.update()
        
        input_sys = g.systems.input_sys
        x, y = self.game.transform.screen_to_world(*input_sys.mouse_pos)
        x, y = int(x), int(y)
        command = self.user_player.command
        
        # プレイヤーを操作する
        if (input_sys.is_keydown(KeyCodes.A)):
            command.move_left()
        if (input_sys.is_keydown(KeyCodes.D)):
            command.move_right()
        
        # debug プレイヤーをワープさせる
        if (input_sys.is_push(KeyCodes.MOUSE_LEFT)):
            self.user_player.x, self.user_player.y = x, y
        # 地形を破壊する
        if (input_sys.is_push(KeyCodes.MOUSE_RIGHT)):
            breaked_list = []
            self.game.world.collision.break_block_in_circle(x, y, self.RADIUS, breaked_list)
            self.game.world.add_particles(breaked_list)
        
        # プレイヤーにダメージを与える
        if (input_sys.is_push(KeyCodes.Z)):
            for col_info in self.game.world.collision.intersect_circle_and_players(x, y, self.RADIUS, self.game.world.player_list):
                player, dist = col_info['player'], col_info['dist']
                
                player.on_you_got_damage(10)
    
    def render(self):
        g.graphics.fill((128, 128, 255))
        self.game.render()
        self.draw_posture_line()

        input_sys = g.systems.input_sys
        x, y = input_sys.mouse_pos
        
        g.graphics.circle((x, y), self.RADIUS, outline=(255, 0, 0))
    
    def draw_posture_line(self):
        player_x, player_y = self.user_player.x, self.user_player.y

        posture_degree = self.game.world.collision.calc_posture_degree(player_x, player_y, True)
        rad = -math.radians(posture_degree)
        
        x0, y0 = Geometry.rotate(-40, 0, rad)
        x1, y1 = Geometry.rotate(40, 0, rad)
        
        p0 = (x0 + player_x, y0 + player_y)
        p1 = (x1 + player_x, y1 + player_y)
        
        g.graphics.line((0, 255, 0), p0, p1)

if __name__ == '__main__':
    import main
    main.main(Scene_TryCollision2(), window_width=1200)