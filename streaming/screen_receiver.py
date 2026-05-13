# ===== Receiver - Low Latency Display =====
import socket
import struct
import time
import cv2
import numpy as np
import threading

BUFFER_SIZE = 2048
TIMEOUT = 0.15
class ScreenReceiver:
    def __init__(self,listen_ip:str, listen_port:int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_ip, listen_port))
        # עדיף buffer לא ענק מדי כדי שלא יצטבר תור ישן
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 512 * 1024)
        self.frames = {}
        self.latest_displayed_frame_id = -1
        self.displayed_frames = 0
        self.dropped_old_frames = 0
        self.dropped_timeout_frames = 0
        self.stats_t0 = time.perf_counter()
        self.stop_event = threading.Event()
        self.thread = None
    def cleanup_old_frames(self, now):
        for fid in list(self.frames.keys()):
            if now - self.frames[fid]["last_seen"] > TIMEOUT:
                del self.frames[fid]
                self.dropped_timeout_frames += 1


    def delete_frames_older_than(self, frame_id):
        for fid in list(self.frames.keys()):
            if fid < frame_id:
                del self.frames[fid]
                self.dropped_old_frames += 1


    def display_frame(self, frame, latency_ms):
        cv2.imshow("ANYDESK - Low Latency", frame)
        cv2.waitKey(1)
        self.displayed_frames += 1

        now = time.perf_counter()
        if now - self.stats_t0 >= 1.0:
            fps = self.displayed_frames / (now - self.stats_t0)

            print(
                "Client FPS:",
                round(fps, 2),
                "| Latency ms:",
                round(latency_ms, 1),
                "| Dropped old:",
                self.dropped_old_frames,
                "| Dropped timeout:",
                self.dropped_timeout_frames,
                "| Waiting frames:",
                len(self.frames)
            )

            self.displayed_frames = 0
            self.dropped_old_frames = 0
            self.dropped_timeout_frames = 0
            self.stats_t0 = now
    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    def stop(self):
        self.stop_event.set()
        self.sock.close()
        self.thread.join(timeout=1)
        cv2.destroyAllWindows()
    def run(self):
        cv2.namedWindow("ANYDESK - Low Latency", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(
            "ANYDESK - Low Latency",
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )
        while not self.stop_event.is_set():
            try:
                packet, addr = self.sock.recvfrom(BUFFER_SIZE)
            except OSError:
                break
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
            if frame_id <= self.latest_displayed_frame_id:
                self.dropped_old_frames += 1
                continue

            now = time.perf_counter()

            if frame_id not in self.frames:
                self.frames[frame_id] = {
                    "total_chunks": total_chunks,
                    "chunks": {},
                    "last_seen": now,
                    "send_time": send_time
                }

            self.frames[frame_id]["chunks"][chunk_index] = chunk_data
            self.frames[frame_id]["last_seen"] = now

            self.cleanup_old_frames(now)
            if frame_id not in self.frames:
                continue
            expected = self.frames[frame_id]["total_chunks"]

            if len(self.frames[frame_id]["chunks"]) == expected:
                chunks = self.frames[frame_id]["chunks"]

                if len(chunks) == expected and all(i in chunks for i in range(expected)):
                    jpg_bytes = b"".join(chunks[i] for i in range(expected))

                    arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

                    if frame is not None:
                        latency_ms = (time.perf_counter() - self.frames[frame_id]["send_time"]) * 1000

                        self.latest_displayed_frame_id = frame_id

                        del self.frames[frame_id]
                        self.delete_frames_older_than(frame_id)

                        self.display_frame(frame, latency_ms)
                    else:
                        del self.frames[frame_id]
                else:
                    del self.frames[frame_id] 