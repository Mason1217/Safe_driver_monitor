import socket
import time
import random

TARGET_IP = "127.0.0.1" # Local host
TARGET_PORT = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"開始發送模擬數據到 {TARGET_IP}:{TARGET_PORT} ...")
print("按 Ctrl+C 停止")

try:
    while True:

        alcohol = round(random.uniform(0.0, 0.6), 2)
        rr_interval = random.randint(600, 1100)
        status = 0
        
        msg = f"A:{alcohol},R:{rr_interval},S:{status}"
        
        sock.sendto(msg.encode('utf-8'), (TARGET_IP, TARGET_PORT))
        print(f"已發送: {msg}")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n停止發送")
    sock.close()