import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame, setupToolClasses

# load image
folder = os.path.join('C:\\Users\\A551221\\OneDrive - AF', 'track_images')
image_files = os.listdir(folder)
image_files = ['straight_lanes_calibrate.jpg']
full_filepath = [os.path.join(folder, file) for file in image_files]


look_ahead_dist = 0.20 # m

### Get tools
birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

for fullpath in full_filepath:
    image = cv2.imread(fullpath)

    lane_image = np.copy(image)

    binary, color, sobel, skyview, curve_fit_result = process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter)

    # Calc steering based on look ahead distance
    x = look_ahead_dist
    fl = curve_fit_result['real_left_best_fit_curve']
    fr = curve_fit_result['real_right_best_fit_curve']
    yl = fl[0] * x ** 3 + fl[1] * x ** 2 + fl[2] * x + fl[3]
    yr = fr[0] * x ** 3 + fr[1] * x ** 2 + fr[2] * x + fr[3]
    y_mid_ahead = (yl + yr) / 2 - curveFitter.w/2*curveFitter.kx # wrt the car's center
    print(y_mid_ahead)

    # Show image
    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    # cv2.imshow('color', color)
    # cv2.imshow('sobel', sobel)
    cv2.imshow('curve fit result', curve_fit_result['image'])

    if cv2.waitKey(1000) == 'q':
        continue