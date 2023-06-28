import pygame

import globals as g
from defines import SHOT_RATE_LIST, SHELL_DEF_LIST, ShellType, clamp, play_se


def get_radius_and_damage(type):
    for shell_def in SHELL_DEF_LIST:
        if (type == shell_def[0]):
            return shell_def[1], shell_def[2]
    return 0, 0

class Shell:

    @classmethod
    def create_shell(cls, shell_type, owner, world, x, y, velocity):
        
        if (shell_type == ShellType.WARP):
            return Shell_Warp(shell_type, owner, world, x, y, velocity)
        else:
            return Shell(shell_type, owner, world, x, y, velocity)
        
        assert False, f"shell_type={type}"
        
        return None
    
    def __init__(self, type, owner, world, x, y, velocity):
        self.type = type
        self.owner = owner
        self.world = world
        self.x, self.y = x, y
        self.radius, self.damage = get_radius_and_damage(type)
        self.velocity = velocity
        self.old_rotate_deg = 0 # 一部の弾でグラフィック描画用に使う
        self.remain_velocity = pygame.Vector2()
        self.kill = False
        self.airtimer = g.systems.time_sys.create_world_timer()
        self.airtimer.timestamp() # タイマーここで始めちゃう
    
    # 滞空時間を返す
    def airtime(self):
        return self.airtimer.elapsed_time
    
    # 滞空時間から、攻撃力と攻撃範囲のレートを取得する
    def power_rate(self):
        sec = self.airtime() * 0.001

        for shot_rate in SHOT_RATE_LIST:
            if (sec >= shot_rate[0]):
                return shot_rate[1], shot_rate[2]

        return 0, 0
    
    def is_kill(self):
        return self.kill
    
    def update(self):
    
        if (self.kill): return
        
        if self.world.collision.check_shell_lost(self.x, self.y):
            self.kill = True
            return
        
        # 移動（なんとなくx, yを整数値にしておく）
        vx, vy = self.velocity + self.remain_velocity
        vx_i, vy_i = int(vx), int(vy)
        self.remain_velocity.update(vx - vx_i, vy - vy_i)
        x = self.x + vx_i; y = self.y + vy_i

        hit, x, y = self.world.collision.intersect_ground_and_line_segment(self.x, self.y, vx_i, vy_i)
        
        if (hit):
            self.on_land(x, y)
        
        self.x = x
        self.y = y
        
        # テキトーに物理的な計算
        self.velocity = (self.velocity[0] * 0.996 + self.world.windy.get_scale() * 0.03,
                            self.velocity[1] + 0.125) # 重力

    # 弾が地面に当たった！
    def on_land(self, x, y):
    
        atk_rate, range_rate = self.power_rate()
        r = int(self.radius * range_rate)
        
        self.hittest(x, y, r, atk_rate)
        
        # 地形を破壊する
        breaked_list = []
        self.world.collision.break_block_in_circle(x, y, r, breaked_list)
        self.world.add_particles(breaked_list)

        self.kill = True
        
        play_se(g.systems, "se_explode")
    
    def hittest(self, x, y, radius, attack_rate):
        # radius内のキャラクターにダメージを与える
        for collide_data in self.world.collision.intersect_circle_and_players(x, y, radius, self.world.player_list):
        
            player = collide_data['player']
            d = collide_data['dist']
            
            # 爆発の中心に近いほど数値が大きくなる(0.0～1.0)
            damage_rate = 1 - (d / radius)
            damage_rate *= 1.75 # 距離が少し離れただけでダメージが小さくなるので、ダメージを出やすくする
            damage_rate = clamp(damage_rate, 0, 1)
            
            # ダメージ(2～)
            damage = max(int(self.damage * attack_rate * damage_rate), 2)
            # ダメージイベントを送信
            player.on_you_got_damage(damage)

# ワープ弾の処理
class Shell_Warp(Shell):
    # 弾が地面に着弾した時の処理
    def on_land(self, x, y):
        # ワープ弾を撃ったプレイヤーを移動させる
        self.owner.x, self.owner.y = x, y
        self.kill = True

        play_se(g.systems, "se_warp")
