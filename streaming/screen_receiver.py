# ===== Receiver - Low Latency Display =====
import socket
import struct
import time
import cv2
import numpy as np

LISTEN_IP = "192.168.2.16"
LISTEN_PORT = 9999

BUFFER_SIZE = 2048
TIMEOUT = 0.15

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, LISTEN_PORT))

# עדיף buffer לא ענק מדי כדי שלא יצטבר תור ישן
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 512 * 1024)

frames = {}
latest_displayed_frame_id = -1

displayed_frames = 0
dropped_old_frames = 0
dropped_timeout_frames = 0

stats_t0 = time.perf_counter()


def cleanup_old_frames(now):
    global dropped_timeout_frames

    for fid in list(frames.keys()):
        if now - frames[fid]["last_seen"] > TIMEOUT:
            del frames[fid]
            dropped_timeout_frames += 1


def delete_frames_older_than(frame_id):
    global dropped_old_frames

    for fid in list(frames.keys()):
        if fid < frame_id:
            del frames[fid]
            dropped_old_frames += 1


def display_frame(frame, latency_ms):
    global displayed_frames, stats_t0
    global dropped_old_frames, dropped_timeout_frames

    cv2.imshow("ANYDESK - Low Latency", frame)
    cv2.waitKey(1)

    displayed_frames += 1

    now = time.perf_counter()
    if now - stats_t0 >= 1.0:
        fps = displayed_frames / (now - stats_t0)

        print(
            "Client FPS:",
            round(fps, 2),
            "| Latency ms:",
            round(latency_ms, 1),
            "| Dropped old:",
            dropped_old_frames,
            "| Dropped timeout:",
            dropped_timeout_frames,
            "| Waiting frames:",
            len(frames)
        )

        displayed_frames = 0
        dropped_old_frames = 0
        dropped_timeout_frames = 0
        stats_t0 = now


while True:
    packet, addr = sock.recvfrom(BUFFER_SIZE)

    # header size:
    # I = 4 bytes
    # H = 2 bytes
    # H = 2 bytes
    # d = 8 bytes
    # total = 16 bytes
    if len(packet) < 16:
        continue

    header = packet[:16]
    chunk_data = packet[16:]

    frame_id, chunk_index, total_chunks, send_time = struct.unpack("!IHHd", header)

    # אם זה פריים ישן שכבר לא מעניין אותנו
    if frame_id <= latest_displayed_frame_id:
        dropped_old_frames += 1
        continue

    now = time.perf_counter()

    if frame_id not in frames:
        frames[frame_id] = {
            "total_chunks": total_chunks,
            "chunks": {},
            "last_seen": now,
            "send_time": send_time
        }

    frames[frame_id]["chunks"][chunk_index] = chunk_data
    frames[frame_id]["last_seen"] = now

    cleanup_old_frames(now)

    expected = frames[frame_id]["total_chunks"]

    if len(frames[frame_id]["chunks"]) == expected:
        chunks = frames[frame_id]["chunks"]

        if len(chunks) == expected and all(i in chunks for i in range(expected)):
            jpg_bytes = b"".join(chunks[i] for i in range(expected))

            arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            if frame is not None:
                latency_ms = (time.perf_counter() - frames[frame_id]["send_time"]) * 1000

                latest_displayed_frame_id = frame_id

                del frames[frame_id]
                delete_frames_older_than(frame_id)

                display_frame(frame, latency_ms)
            else:
                del frames[frame_id]
        else:
            del frames[frame_id]