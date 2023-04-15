import globals as g

# python -m trial.debug_sys を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/debug_sys.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_TryDebugSys:

    def prepare(self):
        pass
    
    def update(self):
        g.systems.debug_sys.text("Try DebugSys!!", (255, 255, 255), background=(0, 0, 0))
        g.systems.debug_sys.text("RED（textalign=center）", (255, 128, 128), background=(0, 0, 0), textalign="center")
        g.systems.debug_sys.text(f"Shadow Color", (128, 255, 128))
    
    def render(self):
        pass

if __name__ == '__main__':
    import main
    main.main(Scene_TryDebugSys(), window_width = 1200)