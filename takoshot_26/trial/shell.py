import globals as g
import main
from core.input_sys import KeyCodes
from core.scene import Scene
from defines import ShellType, StageId
from game import Game


# ワールドに弾を発生させて挙動やグラフィックをテストする
#
# python -m trial.shell を入力し実行
class Scene_TryShell(Scene):

    def __init__(self):
        super().__init__(g.systems)
    
    def prepare(self):
        self.game = Game()
        self.reset_game()
        self.shell_type_index = 0
        self.shell_type_list = ShellType.get_types()
    
    def reset_game(self):
        self.game.create_world(StageId.MOKUZAI)
        
        self.selected_player = self.game.world.add_player(200, 200)
        self.game.world.add_player(400, 100)
    
    def update(self):
    
        input_sys = g.systems.input_sys
        x, y = self.game.transform.screen_to_world(*input_sys.mouse_pos)
        x, y = int(x), int(y)

        if (input_sys.is_push(KeyCodes.KEY_1)):
            self.reset_game()
            return
        
        if (input_sys.is_push(KeyCodes.MOUSE_LEFT)):
            self.game.world.add_shell(self.get_shell_type(), self.selected_player, x, y, (4, -8))
        if (input_sys.is_push(KeyCodes.MOUSE_RIGHT)):
            self.game.world.add_shell(self.get_shell_type(), self.selected_player, x, y, (0, -8))
        
        if (input_sys.is_push(KeyCodes.Z)):
            self.shell_type_index = (self.shell_type_index + 1) % len(self.shell_type_list)
        
        self.game.update()
    
    def render(self):
    
        g.graphics.fill((160, 192, 255))
        self.game.render()

        g.systems.debug_sys.text(f"shell_type={self.get_shell_type()}", (255, 255, 255))
    
    def get_shell_type(self):
        return self.shell_type_list[self.shell_type_index]

if __name__ == '__main__':
    main.main(Scene_TryShell, window_width=1200)
