import globals as g


class Scene:

    class Result:
        NONE    = "none"
        OK      = "ok"
        CANCEL  = "cancel"
    
    def __init__(self, id = None):
        self.id = id
        self.result_type = Scene.Result.NONE
        self.last_update_time_ms = -1 # 最後に更新した時間を保存するために追加（デバッグ用
    
    def prepare(self):
        pass

    def dispose(self):
        pass
    
    def update(self):
        pass
    
    def render(self):
        pass

    def is_exclusive(self):
        return True
    
    def has_result(self):
        return self.result_type != self.Result.NONE

    def has_result_ok(self):
        return self.result_type == self.Result.OK
    
    def end_scene(self, result_type = None, result_param = None):
        self.result_type  = result_type or self.Result.OK
        self.result_param = result_param


# このクラスを継承したサブクラスは
# on_update, on_render, on_end_child_scene, is_exclusive
# を必要に応じてオーバーライドすること
class Scene_Container(Scene):

    def __init__(self, id):
        super().__init__(id)
        
        self.children = []
    
    def update(self):
    
        # 排他的な子シーンなら、親シーンを更新せず終了
        if (self.update_children()): return True
        
        # 自分自身の処理
        self.on_update()
        
        return False
    
    def update_children(self):
        
        # 子どもたちの処理
        snapshot = reversed(self.children)
        
        for child in snapshot:
        
            exclusive = child.update()
            # シーンを更新したら更新時間を書き込む
            if(not exclusive): child.last_update_time_ms = g.systems.time_sys.sys_time_ms
            
            if (child.has_result()):
                # 子シーンを削除
                self.children.remove(child)
                child.dispose()
                
                # 親シーンに子シーン削除イベントを発生させる
                self.on_end_child_scene(child)
            
            # 排他的なシーンなら他のシーンの更新はせず終了
            if (child.is_exclusive() or exclusive):
                return True
        
        return False
    
    def render(self):
        self.on_render()
        
        for child in self.children:
            child.render()
    
    def add_child(self, child):
        child.prepare()
        self.children.append(child)
    
    # 必要ならサブクラス側でオーバーライドしてください
    def on_update(self):
        pass
    
    # 必要ならサブクラス側でオーバーライドしてください
    def on_render(self):
        pass
    
    # 必要ならサブクラス側でオーバーライドしてください
    def on_end_child_scene(self, child_scene):
        pass
