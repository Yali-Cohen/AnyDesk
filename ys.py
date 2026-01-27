import time
from mss import mss

frames = 0
t0 = time.perf_counter()

with mss() as sct:
    mon = sct.monitors[1]
    print(mon["width"], mon["height"])
    half = {"top": 0, "left": 0, "width": mon["width"]//2, "height": mon["height"]//2}

    while True:
        sct.grab(half)
        frames += 1
        t1 = time.perf_counter()
        if t1 - t0 >= 1.0:
            print("FPS:", frames/(t1-t0))
            frames = 0
            t0 = t1
