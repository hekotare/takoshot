from core.input_sys import InputSys
from core.time_sys import TimeSys

class Systems:
    
    def __init__(self):

        self.time_sys = TimeSys()
        self.time_sys.init()
        
        self.input_sys = InputSys()
        self.input_sys.init(self.time_sys)
    
    def begin_process(self):
        self.input_sys.process_key()
    
    def end_process(self):
        self.input_sys.end_process()
        self.time_sys.step_sys_frame()
