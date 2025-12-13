import numpy as np
from collections import deque

ALCOHOL_LIMIT           = 0.25
HRV_FATIGUE_THRESHOLD   = 30
HRV_BUFFER_SIZE         = 30

class DataAnalyzer():
    def __init__(self):
        self.rr_buffer = deque(maxlen=HRV_BUFFER_SIZE)
    
    def parse_raw_data(self, text: str) -> dict:
        '''
        Parse string from server.\n
        Expecting format = "A:0.05,R:800,S:0"

        Returns:
            each value(dict): {"alcohol": 0.0, "rr_interval": 0, "button_status": 0, "valid": False}

        '''
        data = {
            "alcohol": 0.0,
            "rr_interval": 0,
            "button_status": 0,
            "valid": False,
        }

        try:
            parts = text.strip().split(',')

            for part in parts:
                if ':' not in part: continue # no value

                key, val = part.split(':', 1)

                if key == 'A':
                    data["alcohol"] = float(val)
                elif key == 'R':
                    data["rr_interval"] = int(val)
                elif key == 'S':
                    data["button_status"] = int(val)
            
            data["valid"] = True
        
        except ValueError as e:
            print(f"[DataAnalyzer] 數據格式錯誤: {text} -> {e}")
        except Exception as e:
            print(f"[DataAnalyzer] 解析未預期錯誤: {e}")
        
        return data

    def cal_hrv(self, rr_val: int) -> float:
        '''
        Receive new RR interval ,then update buffer and calculate HRV (SDNN).\n
        Note: SDNN = Standard Deviation of NN intervals.

        Returns:
            hrv_sdnn(float): 

        '''
        if rr_val <= 0 or rr_val > 2000:
            return 0.0
        
        self.rr_buffer.append(rr_val)

        if len(self.rr_buffer) < 5:
            return 0.0
        
        # ddof = 1 for sample standard deviation
        hrv_sdnn = np.std(self.rr_buffer, ddof=1)

        return round(hrv_sdnn, 2)
    
    def get_fatigue_status(self, hrv_score: float) -> str:
        '''
        Return status(Normal \ Fatigued) according to given hrv_score.

        '''
        if hrv_score == 0:
            return "Analyzing..."
        
        if hrv_score < HRV_FATIGUE_THRESHOLD:
            return "Fatigued"

        return "Normal"

    def get_alcohol_status(self, alcohol_val: float) -> str:
        '''
        Return status(Normal \ Drunk) according to given alcohol_val.

        '''
        if alcohol_val > ALCOHOL_LIMIT:
            return "Drunk"
        
        return "Normal"
    
    def process(self, raw_text: str):
        '''
        Return final information dictionary from given raw data.

        Returns:
            info(dict):
                {
                    "alcohol_val": ,
                    "rr_val": ,
                    "hrv_val": ,
                    "fatigue_status": ,
                    "alcohol_status": ,
                    "raw_data": ,
                }
            or None

        '''
        parsed = self.parse_raw_data(raw_text)

        if not parsed["valid"]:
            return None
        
        hrv = self.cal_hrv(parsed["rr_interval"])
        fatigue_status = self.get_fatigue_status(hrv)
        alcohol_status = self.get_alcohol_status(parsed["alcohol"])

        return {
            "alcohol_val": parsed["alcohol"],
            "rr_val": parsed["rr_interval"],
            "hrv_val": hrv,
            "fatigue_status": fatigue_status,
            "alcohol_status": alcohol_status,
            "raw_data": parsed,
        }