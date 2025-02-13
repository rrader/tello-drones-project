import os

import cv2
import numpy as np

CLOSE_DISTANCE = 100
ALPHA = 0.3
BETA = 0.1

DIR = os.path.dirname(__file__)

new_scene = True


objects = []


def find_objects():
    global img, kernel, hierarchy, contour, area, ignore, M, center
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # erode and dilate
    img_f = img
    img_f = cv2.erode(img_f, np.ones((5, 5), np.uint8), iterations=5)
    img_f = cv2.dilate(img_f, np.ones((5, 5), np.uint8), iterations=5)
    # blur and canny
    img_f = cv2.GaussianBlur(img_f, (5, 5), 0)
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    img_f = cv2.filter2D(img_f, -1, kernel)
    img_f = cv2.erode(img_f, np.ones((2, 2), np.uint8), iterations=5)
    img_f = cv2.dilate(img_f, np.ones((2, 2), np.uint8), iterations=5)
    img_f = cv2.Canny(img_f, 200, 500)
    contours, hierarchy = cv2.findContours(img_f, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hulls = []
    for contour in contours:
        # contour length
        arclen = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)

        # if at least 5 points
        if len(contour) > 5:
            hull = cv2.convexHull(contour)
            hulls.append(hull)

    # merge intersecting hulls
    hulls2 = hulls.copy()
    for hull1 in hulls:
        ignore = False
        for hull2 in hulls2:
            if hull1 is hull2:
                continue

            # center of a hull
            M = cv2.moments(hull1)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if cv2.pointPolygonTest(hull2, center, False) > 0:
                if cv2.contourArea(hull2) > cv2.contourArea(hull1):
                    # hulls2.remove(hull1)
                    hulls2 = [h for h in hulls2 if h is not hull1]
                    ignore = True
                break

    ret = []
    for hull in hulls2:
        # ignore large objects
        print(cv2.contourArea(hull))
        if cv2.contourArea(hull) > 15000:
            continue
        if cv2.arcLength(hull, True) > 700:
            continue

        # add hull to ret by specifying the center, the area and the hull
        M = cv2.moments(hull)
        rect = cv2.minAreaRect(hull)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        width = np.linalg.norm(box[0] - box[1])
        height = np.linalg.norm(box[1] - box[2])

        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        ret.append({
            "center": center,
            "radius": cv2.arcLength(hull, True) / (2 * np.pi),
            "height": height,
            "width": width,
            "hull": hull
        })
    # cv2.imshow("test", img_f)
    # cv2.waitKey(0)

    return ret



#     img = cv2.imread(f"{DIR}/scene1/{i}.jpg")
while True:
    for i in range(20):
    # for i in [4, 5, 6, 7, 8]:
    # for i in [7, 8]:
        img = cv2.imread(f"{DIR}/scene1/{i}.jpg")

        new_objs = find_objects()
        for nobj in new_objs:
            # find the closest object in `objects`
            closest = 999999999
            closest_obj = None
            for obj in objects:
                dist = cv2.norm(obj['center'], nobj['center'])
                if dist < closest and np.abs(obj['radius'] - nobj['radius']) < 20:
                    closest = dist
                    closest_obj = obj

            if closest_obj:
                print("adjust")
                closest_obj['center'] = (
                    closest_obj['center'][0] + (nobj['center'][0] - closest_obj['center'][0]) * ALPHA,
                    closest_obj['center'][1] + (nobj['center'][1] - closest_obj['center'][1]) * ALPHA
                )
                rdiff = (nobj['radius'] - closest_obj['radius']) / closest_obj['radius']
                closest_obj['radius'] = closest_obj['radius'] + (nobj['radius'] - closest_obj['radius']) * BETA
                closest_obj['height'] = closest_obj['height'] + (nobj['height'] - closest_obj['height']) * BETA
                closest_obj['width'] = closest_obj['width'] + (nobj['width'] - closest_obj['width']) * BETA
                closest_obj['power'] += 1
                closest_obj['accuracy'] = np.average([(float(closest) / img.shape[0]) * 3, rdiff * 3, closest_obj['accuracy']])
            else:
                # add new object
                print('new obj')
                objects.append(nobj)
                nobj['power'] = 2
                nobj['accuracy'] = 0
            # cv2.circle(img, (int(nobj['center'][0]), int(nobj['center'][1])), int(nobj['radius']), (0, 255, 0), 1)

        for obj in objects:
            obj['power'] /= 1.5

        for obj in [obj for obj in objects if obj['power'] < 1]:
            objects.remove(obj)

        for obj in objects:

            cv2.rectangle(img, (int(obj['center'][0] - obj['width'] / 2), int(obj['center'][1] - obj['height'] / 2)),
                            (int(obj['center'][0] + obj['width'] / 2), int(obj['center'][1] + obj['height'] / 2)), (0, 0, 255), int(obj['power']))

            cv2.circle(img,(
                int(obj['center'][0] - (obj['width'] / 2) * (obj['accuracy'] + 1.0)),
                int(obj['center'][1] - (obj['height'] / 2) * (obj['accuracy'] + 1.0)),
                ), int(1), (0, 255, 0), 2)
            cv2.circle(img,(
                int(obj['center'][0] + (obj['width'] / 2) * (obj['accuracy'] + 1.0)),
                int(obj['center'][1] - (obj['height'] / 2) * (obj['accuracy'] + 1.0)),
                ), int(1), (0, 255, 0), 2)
            cv2.circle(img,(
                int(obj['center'][0] - (obj['width'] / 2) * (obj['accuracy'] + 1.0)),
                int(obj['center'][1] + (obj['height'] / 2) * (obj['accuracy'] + 1.0)),
                ), int(1), (0, 255, 0), 2)
            cv2.circle(img,(
                int(obj['center'][0] + (obj['width'] / 2) * (obj['accuracy'] + 1.0)),
                int(obj['center'][1] + (obj['height'] / 2) * (obj['accuracy'] + 1.0)),
                ), int(1), (0, 255, 0), 2)


        cv2.imshow("Image", img)
        k = cv2.waitKey(300) & 0XFF
        if k == 27:
            break
