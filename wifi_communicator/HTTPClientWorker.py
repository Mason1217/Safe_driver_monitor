import time
import requests
from PyQt6.QtCore import QThread, pyqtSignal

class HTTPClientWorker(QThread):
    
    data_received = pyqtSignal(dict)
    log_message = pyqtSignal(str)

    def __init__(self, ip="172.20.10.9", interval=0.5):
        super().__init__()
        self.url = f"http://{ip}/test"
        self.interval = interval
        self.is_running = True

    def run(self):
        self.log_message.emit(f"開始連線至 {self.url} ...")
        
        while self.is_running:
            try:
                response = requests.get(self.url, timeout=2.0)
                
                if response.status_code == 200:
                    json_data = response.json()
                    print(json_data)
                    self.data_received.emit(json_data)
                else:
                    self.data_received.emit(dict())
                    self.log_message.emit(f"連線錯誤: {response.status_code}")

            except requests.exceptions.Timeout:
                self.log_message.emit("連線逾時 (ESP8266 沒回應)")
            except requests.exceptions.ConnectionError:
                self.log_message.emit("無法連線 (請檢查 IP 或 WiFi)")
            except Exception as e:
                self.log_message.emit(f"發生未預期錯誤: {e}")

            time.sleep(self.interval)

    def stop(self):
        self.is_running = False
        self.wait()