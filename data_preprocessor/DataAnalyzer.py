import os
import json
import random
import numpy as np
from collections import deque

HISTORY_FILE = "hrv_history.json"

ALCOHOL_LIMIT           = 0.25
HRV_FATIGUE_THRESHOLD   = 30
HRV_BUFFER_SIZE         = 30

HRV_MAX_BOUND           = 80.0
HRV_MIN_BOUND           = 20.0
DEFAULT_HRV_BASELINE    = 50.0

ALCOHOL_ST = {'N': "Normal", 'D': "Drunk", 'W': "Waiting..."}
FATIGUE_ST = {
    'N': "Normal",
    'F': "Fatigued",
    'A': "Analyzing...",
    'B': "Balanced",
    'U': "Unbalanced",
    'L': "Low",
}

DATA_DICT_KEY = {
    "al": "alcohol",
    "hr": "heart_rate",
    "hrv": "hrv_val",
    "f_idx": "fatigue_index",
    "f_st": "fatigue_status",
    "al_st": "alcohol_status",
    "raw": "raw_data",
    "base": "baseline_hrv"
}

class DataAnalyzer():
    def __init__(self):
        self.rr_buffer = deque(maxlen=HRV_BUFFER_SIZE)
        self.history_data = self.load_history()
        self.baseline_hrv = self.cal_baseline()
        self.today_measurements = []

        print(f"[System] 目前 7 天平均基線 (Baseline): {self.baseline_hrv:.2f}")

    def save_daily_record(self):
        if not self.today_measurements:
            print("[System] 本次運行無有效 HRV 數據，跳過存檔。")
            return
        
        today_avg = int(round(np.mean(self.today_measurements), 2))
        print(f"[System] 本次測量平均 HRV: {today_avg}，正在更新歷史紀錄...")

        self.history_data.append(today_avg)
        if len(self.history_data) > 7:
            self.history_data.pop(0)

        self.save_history(self.history_data)
        print(f"[System] 歷史紀錄已更新 (最近7筆): {self.history_data}")

    def load_history(self) -> list:
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                print(f"讀取歷史失敗: {e}，將建立新檔")
        
        mock_data = [random.randint(50, 70) for _ in range(6)]
        self.save_history(mock_data)

        return mock_data
    
    def save_history(self, data: list):
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"存檔失敗: {e}")

    def cal_baseline(self) -> float:
        if not self.history_data:
            return DEFAULT_HRV_BASELINE
        return float(np.mean(self.history_data))

    def parse_raw_data(self, text: str) -> dict:
        '''
        Parse string from server.\n
        Expecting format = "A:0.05,R:800,S:0"

        Returns:
            each value(dict): {"alcohol": 0.0, "hr": 0, "hrv": 0, "valid": False}

        '''
        data = {
            "alcohol": 0.0,
            "hr": 0,
            "hrv": 0,
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
                    data["hr"] = int(val)
                elif key == "HRV":
                    data["hrv"] = float(val)
            
            data["valid"] = True
        
        except ValueError as e:
            print(f"[DataAnalyzer] 數據格式錯誤: {text} -> {e}")
        except Exception as e:
            print(f"[DataAnalyzer] 解析未預期錯誤: {e}")
        
        return data

    def cal_fatigue_idx(self, hrv_val: float) -> int:
        '''
        Calculate degree of fatigue based on hrv_val

        '''
        if hrv_val == 0: return -1

        if hrv_val <= HRV_MIN_BOUND: return 100
        if hrv_val >= HRV_MAX_BOUND: return 0

        ratio = (hrv_val - HRV_MIN_BOUND) / (HRV_MAX_BOUND - HRV_MIN_BOUND)
        fatigue_idx = (1.0 - ratio) * 100

        return int(fatigue_idx)


    def get_fatigue_status(self, hrv_score: float) -> str:
        '''
        Return status(Normal \ Fatigued) according to given hrv_score.

        '''
        if hrv_score == 0:
            return FATIGUE_ST['A']
        
        if hrv_score < HRV_FATIGUE_THRESHOLD:
            return FATIGUE_ST['F']

        return FATIGUE_ST['B']

    def get_alcohol_status(self, alcohol_val: float) -> str:
        '''
        Return status(Normal \ Drunk) according to given alcohol_val.

        '''
        if alcohol_val is None: return ALCOHOL_ST['W']

        if alcohol_val > ALCOHOL_LIMIT:
            return ALCOHOL_ST['D']
        
        return ALCOHOL_ST['N']
    
    def process(self, raw_text: str):
        '''
        Return final information dictionary from given raw data.

        Returns:
            info(dict): or None

        '''
        parsed = self.parse_raw_data(raw_text)

        if not parsed["valid"]:
            return None
        
        hrv = parsed.get("hrv")
        fatigue_idx = self.cal_fatigue_idx(hrv)
        fatigue_status = self.get_fatigue_status(hrv)
        alcohol_status = self.get_alcohol_status(parsed.get("alcohol"))

        if hrv > 0:
            self.today_measurements.append(hrv)

        return {
            DATA_DICT_KEY["al"]: parsed["alcohol"],
            DATA_DICT_KEY["hr"]: parsed["hr"],
            DATA_DICT_KEY["hrv"]: hrv,
            DATA_DICT_KEY["f_idx"]: fatigue_idx,
            DATA_DICT_KEY["f_st"]: fatigue_status,
            DATA_DICT_KEY["al_st"]: alcohol_status,
            DATA_DICT_KEY["raw"]: parsed,
            DATA_DICT_KEY["base"]: self.baseline_hrv,
        }