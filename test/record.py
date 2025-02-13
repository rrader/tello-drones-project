import os
import time

import cv2
from djitellopy import Tello

DIR = os.path.dirname(__file__)

tello = Tello()
tello.connect()

tello.streamon()
frame_read = tello.get_frame_read()

# make 20 frames
for i in range(20):
    time.sleep(2)
    print("Photo")
    cv2.imwrite(f"{DIR}/scene1/{i}.jpg", frame_read.frame)
