# ===== Client (Receiver) - prints REAL FPS (frames actually displayed) =====
import socket
import struct
import time
import cv2
import numpy as np

BUFFER_SIZE = 2048
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.1.228", 9999))

frames = {}  # frame_id -> {"total_chunks": int, "chunks": dict[int, bytes]}
shown_frames = 0
t0 = time.perf_counter()

def perform_frame(frame):
    global shown_frames, t0

    cv2.imshow("ANYDESK", frame)
    cv2.waitKey(1)

    # Count ONLY frames that were actually decoded+shown
    shown_frames += 1

    t1 = time.perf_counter()
    if t1 - t0 >= 1.0:
        fps = shown_frames / (t1 - t0)
        print("Client REAL FPS:", round(fps, 2))
        shown_frames = 0
        t0 = t1

while True:
    bytes_data, addr = sock.recvfrom(BUFFER_SIZE)
    if len(bytes_data) < 8:
        continue

    header_bytes = bytes_data[:8]
    frame_id, chunk_index, total_chunks = struct.unpack("!IHH", header_bytes)
    chunk_data = bytes_data[8:]

    if frame_id not in frames:
        frames[frame_id] = {"total_chunks": total_chunks, "chunks": {}}

    frames[frame_id]["chunks"][chunk_index] = chunk_data

    expected = frames[frame_id]["total_chunks"]
    if len(frames[frame_id]["chunks"]) == expected:
        # Ensure no missing indices (UDP can drop/reorder)
        if set(frames[frame_id]["chunks"].keys()) == set(range(expected)):
            jpg_bytes = b"".join(frames[frame_id]["chunks"][i] for i in range(expected))
            arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is not None:
                perform_frame(frame)

        del frames[frame_id]