import globals as g
import graphics_ex as gra_ex
import main
from core.input_sys import KeyCodes
from core.scene import Scene


# python -m trial.gra_ex を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/gra_ex.pyを入力し、リモートデバッグ実行
class Scene_TryGraEx(Scene):

    def prepare(self):
        self.timer = g.systems.time_sys.create_sys_timer()
    
    def update(self):
        g.graphics.fill((200, 200, 255))

        input_sys = g.systems.input_sys
        if (input_sys.is_push(KeyCodes.Z)):
            self.timer.start(duration_time_ms=1200)
    
    def render(self):

        if self.timer.enabled():
            gra_ex.draw_next_phase(self.timer.progress)

if __name__ == '__main__':
    main.main(Scene_TryGraEx())
