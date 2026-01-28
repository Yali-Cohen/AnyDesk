import socket
import struct

import cv2
import numpy as np
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("socket closed")
        data += chunk
    return data

def recv_frame_jpeg(sock):
    size = struct.unpack("!I", recv_exact(sock, 4))[0]
    data = recv_exact(sock, size)
    arr = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # יוצא BGR
    return frame
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Hi", ("192.168.2.16", 1010))
data, server_addr = sock.recvfrom(BUFFER_SIZE)
