from defines import CHARA_DATA_LIST


class ChrDataManager:
    
    def __init__(self):
        self.map = {}
    
    def load(self):
    
        self.map = {}
        
        for data in CHARA_DATA_LIST:
            self.register(ChrData(*data))
    
    def register(self, data):
        assert self.map.get(data.type) == None, f"すでに登録済みです type={data.type}"
        
        self.map[data.type] = data
    
    def bmp_name(self, chr_type):
        return self.map[chr_type].bmp_name
    
    def type_list(self):
        return list(self.map.keys())

class ChrData:
    
    def __init__(self, type, bmp_name):
        self.type = type
        self.bmp_name = bmp_name
