import sys
import signal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from wifi_communicator import UDPServerWorker

def handle_data(data):
    print(f"🔥🔥 主程式收到資料: {data}")

def signal_handler(sig, frame):

    print("\n👋 偵測到 Ctrl+C，正在關閉程式...")

    if 'server' in globals():
        server.stop()

    QApplication.quit()

app = QApplication(sys.argv)

signal.signal(signal.SIGINT, signal_handler)

timer = QTimer()
timer.start(500) 
timer.timeout.connect(lambda: None)

server = UDPServerWorker()
server.data_received.connect(handle_data)
server.start()

print("測試程式運行中... (現在按 Ctrl+C 可以正常結束了！)")

sys.exit(app.exec())