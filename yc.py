import socket
import struct
import time

import cv2
import numpy as np
    
BUFFER_SIZE = 2048

def recv_exact(sock):
    flag = True
    data = b""
    while flag:
        chunk, addr = sock.recvfrom(10000)
        data += chunk
        if "IEND" in data:
            flag = False
    return data
def perform_frame(frame):
    cv2.imshow("ANYDESK", frame)
def recv_frame_jpeg(sock):
    bytes_data = sock.recvfrom(BUFFER_SIZE)
    unpacked_data = struct.unpack("!IHH", bytes_data)[0]
    print(unpacked_data)
    # arr = np.frombuffer(data, dtype=np.uint8)
    # frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # יוצא BGR
    # return frame
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hi", ("192.168.2.16", 1010))
while True:
    frame = recv_frame_jpeg(sock)
    time.sleep(2)
    print(frame)
    perform_frame(frame)
