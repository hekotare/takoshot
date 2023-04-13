import globals as g

# python -m trial.actgame を入力し実行
# python -m debugpy --wait-for-client --listen 5678 trial/actgame.py を入力しデバッグ実行（リモートデバッグの設定必要）
class Scene_ActionGame:

    def prepare(self):
        pass
    
    def update(self):
        pass

    def render(self):
        g.graphics.text((360, 20), "Action Game!!", (255, 255, 255), font=g.font_i40, textalign="center")

if __name__ == '__main__':
    import main
    main.main(Scene_ActionGame())