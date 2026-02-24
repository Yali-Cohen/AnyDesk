import socket
import struct
import time

import cv2
import numpy as np
    
BUFFER_SIZE = 2048

def perform_frame(frame):
    cv2.imshow("ANYDESK", frame)
def recv_frame_jpeg(sock):
    bytes_data = sock.recvfrom(BUFFER_SIZE)
    unpacked_data = struct.unpack("!IHH", bytes_data)[0]
    header_bytes = bytes_data[:8]
    chunk_data = bytes_data[8:]
    print(unpacked_data)
    # arr = np.frombuffer(data, dtype=np.uint8)
    # frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # יוצא BGR
    # return frame
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hi", ("10.0.0.30", 1011))
while True:
    frame = recv_frame_jpeg(sock)
    time.sleep(2)
    # print(frame)
    perform_frame(frame)
