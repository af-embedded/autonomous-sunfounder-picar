import cv2
import numpy as np
import os
from LaneTracking import process_one_frame
import matplotlib.pyplot as plt


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
    m_max_actuate = 2
    x_int_max_actuate = 100
    try:
        print(averaged_lines)
        x1, y1, x2, y2 = averaged_line
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m*x1
        x_int_mid = (image.shape[1]-b)/m - image.shape[1]/2
        print('slope', m)
        print('x-intercept', (image.shape[1]-b)/m)
        print('x-int from middle', x_int_mid)


        if m > 0:
            # go straight if slope is high and x-int is on the right
            if abs(m) > m_max_actuate and abs(x_int_mid) > 0:
                print('straight')
                angle = 0
            # turn left if slope is too low or x-int is too left of the image
            else:
                print('turn')
                angle_slope = 0.4 * (m_max_actuate - abs(m)) * angle_max
                angle_x_int = 1 * (x_int_mid_min / max(0.01, x_int_mid)) * angle_max
                angle = max(angle_slope, angle_x_int)
                # print(angle_slope, angle_x_int)
        elif m < 0:
            # go straight if slope is high and x-int is on the right
            if abs(m) > m_max_actuate and abs(x_int_mid) > 0:
                print('straight')
                angle = 0
            # turn right if abs(slope) is too low or x-int is too right of the image
            else:
                print('turn')
                angle_slope = 0.4 * (m_max_actuate - abs(m)) * angle_max
                angle_x_int = 1 * (-x_int_mid_min / min(-0.01, x_int_mid)) * angle_max
                angle = max(angle_slope, angle_x_int)

    except:
        print('no averaged line')

    print(angle)
    angle = angle + 90
    angle = max(min(angle, 135), 45)

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(100000) == 'q':
        continue