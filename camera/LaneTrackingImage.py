import cv2
import numpy as np
import os
from LaneTracking import process_one_frame
import matplotlib.pyplot as plt
import math

# load image
this_file_path = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(this_file_path, 'test_images')
image_files = os.listdir(folder)


for filename in image_files:
    image = cv2.imread(os.path.join(folder, filename))

    lane_image = np.copy(image)

    output_image, canny_image, averaged_lines, averaged_line = process_one_frame(image)

    angle = 0
    angle_max = 45
    x_int_mid_min = 50
    x_int_max_actuate = 100
    try:
        print(averaged_lines)
        x1, y1, x2, y2 = averaged_line
        m = (y2 - y1) / (x2 - x1)
        m_angle = math.degrees(math.atan(1 / m))  # left is positive
        b = y1 - m * x1
        x_int_mid = (image.shape[1] - b) / m - image.shape[1] / 2
        print('slope', m)
        print('x-intercept', (image.shape[1] - b) / m)
        print('x-int from middle', x_int_mid)

        if m_angle > 0:
            # go straight if x-int is too far right
            if x_int_mid > x_int_max_actuate:
                print('straight')
                angle = 0
            # turn left
            else:
                print('turn')
                angle = m_angle
        elif m_angle < 0:
            # go straight if x-int is on the left
            if x_int_mid < -x_int_max_actuate:
                print('straight')
                angle = 0
            # turn right
            else:
                print('turn')
                angle = -m_angle
        else:
            print('straight')
            angle = 0

    except:
        print('no averaged line')

    # Actuate, angles in the car go from 45 (full left) to 135 (full right)
    angle = angle + 90
    angle = max(min(angle, 135), 45)
    print(angle)

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(100000) == 'q':
        continue