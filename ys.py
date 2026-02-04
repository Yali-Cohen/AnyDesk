# import time
# import cv2
# from mss import mss
# import numpy as np

# frames = 0
# t0 = time.perf_counter()

# with mss() as sct:
#     mon = sct.monitors[1]
#     print(mon["width"], mon["height"])
#     half = {"top": 0, "left": 0, "width": mon["width"]//2, "height": mon["height"]//2}

#     while True:
#         sct_img = sct.grab(half)
#         img = np.array(sct_img)
#         img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
#         cv2.imshow("Screen Capture", img_bgr)
#         frames += 1
#         t1 = time.perf_counter()
#         if t1 - t0 >= 1.0:
#             print("FPS:", frames/(t1-t0))
#             frames = 0
#             t0 = t1
import cv2
import numpy as np
from mss import mss
import time
import struct
import socket 
from threading import Thread
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.2.16", 1010))

def send_frame_jpeg(sock, frame_bgr, quality=70):
    ok, enc = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return
    data = enc.tobytes()
    sock.sendall(struct.pack("!I", len(data)) + data)
def capture_screen(sock):
    frames = 0
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
            print(frame)
            send_frame_jpeg(sock, frame)
            # bgr_image_np = cv2.imread(frame)

            # # Check if the image was loaded correctly
            # if bgr_image_np is None:
            #     print("Error loading image")
            # else:
            #     # 2. Convert the NumPy array to a bytes object
            #     # This creates a contiguous stream of B, G, R, B, G, R... bytes
            #     image_bytes = bgr_image_np.tobytes()
            #     print(image_bytes)
            # Display the frame in a window
            cv2.imshow("MSS Streaming", frame)
            frames += 1
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