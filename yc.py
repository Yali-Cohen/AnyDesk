import socket
import struct
import time

import cv2
import numpy as np
    
BUFFER_SIZE = 2048
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("10.0.0.39", 9999))


def perform_frame(frame):
    cv2.imshow("ANYDESK", frame)
    cv2.waitKey(1)
def recv_frame_jpeg(sock, frames):
    bytes_data, addr = sock.recvfrom(BUFFER_SIZE)
    header_bytes = bytes_data[:8]
    frame_id, chunk_index, total_chunks = struct.unpack("!IHH", header_bytes)
    chuck_data = bytes_data[8:]
    if frame_id not in frames:
        frames[frame_id] = {"total_chunks": total_chunks, "chunks": {}}
        frames[frame_id]["chunks"][chunk_index] = chuck_data
        if len(frames[frame_id]["chunks"]) == frames[frame_id]["total_chunks"]:
            jpg_bytes = b"".join(frames[frame_id]["chunks"][i] for i in range(frames[frame_id]["total_chunks"]))
            arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # יוצא BGR
            perform_frame(frame)
            del frames[frame_id]  # ניקוי הזיכרון
    else:
        frames[frame_id]["chunks"][chunk_index] = chuck_data
        if len(frames[frame_id]["chunks"]) == frames[frame_id]["total_chunks"]:
            jpg_bytes = b"".join(frames[frame_id]["chunks"][i] for i in range(total_chunks))
            arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # יוצא BGR
            perform_frame(frame)
            del frames[frame_id]  # ניקוי הזיכרון
    
    # arr = np.frombuffer(data, dtype=np.uint8)
    # frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)  # יוצא BGR
    # return frame
frames = {} # frame_id -> frame_state

while True:
    recv_frame_jpeg(sock, frames)    
