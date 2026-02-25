import cv2
import numpy as np
from mss import mss
import time
import struct
import socket 
from threading import Thread
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_frame_jpeg(sock, frame_bgr,frame_id, quality=70):
    ok, enc = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return
    jpg_bytes = enc.tobytes()
    CHUNK = 1200  
    chunks = [jpg_bytes[i:i+CHUNK] for i in range(0, len(jpg_bytes), CHUNK)]
    for i, chunk in enumerate(chunks):
        chunk_id = i
        payload = {
            "frame_id": frame_id,
            "chunk_index": chunk_id,
            "total_chunks": len(chunks),
        }
        header_bytes = struct.pack("!IHH", payload["frame_id"], payload["chunk_index"], payload["total_chunks"])
        packet = header_bytes + chunk
        sock.sendto(packet, ("192.168.2.16", 9999))

def capture_screen(sock):
    frames = 0
    frame_id_counter = 0
    t0 = time.perf_counter()
    with mss() as sct:
        mon = sct.monitors[1]
        half = {"top": 0, "left": 0, "width": mon["width"]//2, "height": mon["height"]//2}
        while True:
            # Grab the screen data
            sct_img = sct.grab(half)
            # Convert the raw pixels to a NumPy array and then to BGR format for OpenCV
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR) # Convert BGRA to BGR
            send_frame_jpeg(sock, frame, frame_id=frame_id_counter)
            frames += 1
            frame_id_counter += 1
            t1 = time.perf_counter()
            if t1 - t0 >= 1.0:
                print("FPS:", frames/(t1-t0))
                frames = 0
                t0 = t1
            # Press 'q' to quit the streaming loop
            if cv2.waitKey(1) == ord('q'):
                break

        cv2.destroyAllWindows()
t1 = Thread(target=capture_screen, args=(sock,))
t1.start()
t1.join()