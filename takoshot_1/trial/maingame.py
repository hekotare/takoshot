# python -m trial.maingame を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/maingame.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_MainGame:

    def prepare(self):
        pass
    
    def update(self):
        pass

    def render(self):
        pass

if __name__ == '__main__':
    import main
    main.main(Scene_MainGame())