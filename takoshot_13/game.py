import globals as g
import graphics_ex as gra_ex
from entity.world import World


class Game:

    def __init__(self):
        self.sight = Sight()
        self.sight_player = None
    
    def load(self):
        self.world = World()
        self.world.add_player(140, 150)
        self.world.add_player(340, 150)
    
    def create_world(self):
        self.world = World()
    
    def update(self):
        self.world.update()

    def render(self):
    
        world = self.world
        
        gra_ex.draw_stage(world.stage)
        
        # キャラクタの照準
        self.sight.update()
        
        gra_ex.draw_player_sight(self.sight_player, self.sight.scale)
        
        for player in world.player_list:
            gra_ex.draw_player(player)
        
        for shell in world.shell_list:
            gra_ex.draw_shell(shell)
        
        #---------------------------------
        # debug
        #---------------------------------
        if g.DebugFlags.DISPLAY_PLAYER_MUZZLE_POSITION:
            for player in self.world.player_list:
                gra_ex.draw_player_muzzle_position(g.surface, player)
    
    # 試合が決着しているか判定する
    def check_game_finished(self):
    
        # 生存者チェック
        alive_players = [player for player in self.world.player_list if player.is_alive()]
        num_of_alive = len(alive_players)
        
        if (num_of_alive in [0, 1]): # 全員死亡した or 一人が生き残った
            return True, alive_players
        
        return False, []

    def open_sight(self, player):
        self.sight.open()
        self.sight_player = player

    def close_sight(self):
        self.sight.close()

# プレイヤーの照準
class Sight:

    class State:
        Opening = "opening"
        Open    = "open"
        Closing = "closing"
        Closed  = "closed"
    
    def __init__(self):
        self.player = None
        self.state = self.State.Closed
        self.scale = 0.0
        self.timer = g.systems.time_sys.create_sys_timer()
    
    def open(self):
        self.state = self.State.Opening
        self.timer.start(duration_time_ms=250)
    
    def close(self):
        self.state = self.State.Closing
        self.timer.start(duration_time_ms=250)

    def update(self):
        if (self.state == self.State.Opening):
        
            if (self.timer.is_finished()):
                self.state = self.State.Open

            self.scale = self.timer.progress
            
        elif (self.state == self.State.Closing):
        
            if (self.timer.is_finished()):
                self.state = self.State.Closed
            
            self.scale = 1.0 - self.timer.progress
