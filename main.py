import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from wifi_communicator import UDPServerWorker
from data_preprocessor import DataAnalyzer
from visualizer import MonitorWindow

class SystemController:
    def __init__(self):
        self.analyzer = DataAnalyzer()
        self.window = MonitorWindow()
        self.server = UDPServerWorker()

        self.server.data_received.connect(self.handle_new_data)
        self.server.log_message.connect(lambda msg: print(f"[System] {msg}"))

    def start(self):
        self.window.show()
        self.server.start()
        
        print("★ 系統啟動完成，視窗已顯示，正在背景監聽 UDP Port 8888...")
    
    def stop(self):
        print("★ 正在保存今日測量結果...")
        self.analyzer.save_daily_record()

        if self.server.is_running:
            self.server.stop()
        
        print("★ 系統已安全關閉。")
    
    def handle_new_data(self, raw_text):
        processed_data = self.analyzer.process(raw_text)

        if processed_data:
            self.window.update_display(processed_data)
        else:
            print(f"收到無效數據: {raw_text}")

def main():
    app = QApplication(sys.argv)
    controller = SystemController()

    def signal_handler(sig, frame):
        print("\n👋 偵測到 Ctrl+C，正在關閉程式...")
        controller.stop()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)

    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    controller.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()