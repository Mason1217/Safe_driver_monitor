import socket
from PyQt6.QtCore import QThread, pyqtSignal

DEBUG = 0

class UDPServerWorker(QThread):
    '''
    Monitors UDP packets in background.
    When receives data from ESP8266, send to main program through Signal.

    '''
    data_received = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, host="0.0.0.0", port=8888):
        super().__init__()
        self.host = host
        self.port = port
        self.is_running = True
        self.socket = None

    def run(self):
        '''
        Run this function automatically when thread activated.

        '''
        self.log_message.emit(f"正在啟動 UDP Server 於 {self.port} 埠口...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.host, self.port))
            self.log_message.emit("伺服器啟動成功，等待 ESP8266 資料中...")

            while self.is_running:
                try:
                    self.socket.settimeout(1.0)
                    data, addr = self.socket.recvfrom(1024)
                    text_data = data.decode('utf-8').strip()
                    self.data_received.emit(text_data)
                    
                    if DEBUG:
                        print(f"[{addr[0]}] 收到: {text_data}")

                except socket.timeout:
                    continue
                except Exception as e:
                    self.log_message.emit(f"接收資料錯誤: {e}")

        except Exception as e:
            self.log_message.emit(f"無法啟動 Server: {e}")
        finally:
            self.stop()

    def stop(self):
        '''
        Close server safely
        
        '''
        self.is_running = False

        if self.socket:
            self.socket.close()
            
        self.log_message.emit("伺服器已關閉")