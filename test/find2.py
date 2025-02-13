import os

import cv2
import numpy as np

# FOV is 74 deg
CLOSE_DISTANCE = 100
ALPHA = 0.3
BETA = 0.1

DIR = os.path.dirname(__file__)

new_scene = True


objects = []


#     img = cv2.imread(f"{DIR}/scene1/{i}.jpg")
while True:
    # for i in range(20):
    for i in [4]:
    # for i in [7, 8]:
        img = cv2.imread(f"{DIR}/scene1/{i}.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        cv2.imshow("Image", img)
        k = cv2.waitKey(300) & 0XFF
        if k == 27:
            break
