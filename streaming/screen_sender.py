# ===== Sender - Low Latency Screen Stream =====
import math

import cv2
import numpy as np
from mss import mss
import time
import struct
import socket
import threading
WIDTH = 960
HEIGHT = 540
JPEG_QUALITY = 45
TARGET_FPS = 20

CHUNK_SIZE = 1200
class ScreenSender:
    def __init__(self, target_ip:str, target_port:int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)
        self.stop_evt = threading.Event()
        self.TARGET_IP = target_ip
        self.TARGET_PORT = target_port
        self.thread = None

    def start(self):
        self.stop_evt.clear()
        self.thread = threading.Thread(target=self.capture_screen, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_evt.set()
        if self.thread not in None:
            self.thread.join()

    def send_frame_jpeg(self, frame_bgr, frame_id, quality=45):
        ok, enc = cv2.imencode(
            ".jpg",
            frame_bgr,
            [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        )

        if not ok:
            return 0

        jpg_bytes = enc.tobytes()
        total_chunks = math.ceil(len(jpg_bytes) / CHUNK_SIZE)

        send_time = time.perf_counter()

        for chunk_index in range(total_chunks):
            start = chunk_index * CHUNK_SIZE
            end = start + CHUNK_SIZE
            chunk = jpg_bytes[start:end]

            # frame_id: unsigned int
            # chunk_index: unsigned short
            # total_chunks: unsigned short
            # send_time: double
            # !  = network byte order (bytes will be ordered big-endian)
            # I  = unsigned int, 4 bytes
            # H  = unsigned short, 2 bytes
            # H  = unsigned short, 2 bytes
            # d  = double, 8 bytes
            header = struct.pack("!IHHd", frame_id, chunk_index, total_chunks, send_time)

            self.sock.sendto(header + chunk, (self.TARGET_IP, self.TARGET_PORT))

        return len(jpg_bytes)


    def capture_screen(self):
        frame_id = 0
        shown_fps_counter = 0
        t0 = time.perf_counter()

        frame_interval = 1 / TARGET_FPS

        with mss() as sct:
            mon = sct.monitors[1]
            print("Original monitor:", mon["width"], "x", mon["height"])

            while not self.stop_evt.is_set():
                loop_start = time.perf_counter()

                sct_img = sct.grab(mon)
                frame = np.array(sct_img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                resized = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)

                size = self.send_frame_jpeg(resized, frame_id, JPEG_QUALITY)

                frame_id += 1
                shown_fps_counter += 1

                now = time.perf_counter()
                if now - t0 >= 1.0:
                    print(
                        "Sender FPS:",
                        round(shown_fps_counter / (now - t0), 2),
                        "| Last JPG KB:",
                        round(size / 1024, 1)
                    )
                    shown_fps_counter = 0
                    t0 = now

                elapsed = time.perf_counter() - loop_start
                sleep_time = frame_interval - elapsed

                if sleep_time > 0:
                    time.sleep(sleep_time)


