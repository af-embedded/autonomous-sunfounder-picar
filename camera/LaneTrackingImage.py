import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame, setupToolClasses

# load image
# folder = os.path.join('C:\\Users\\horac\\OneDrive - AF', 'poor_performance_images')
folder = os.path.join('C:\\Users\\horac\\OneDrive - AF', 'track_images')
# image_files = os.listdir(folder)
image_files = ['straight_lanes_calibrate.jpg']
full_filepath = [os.path.join(folder, file) for file in image_files]


look_ahead_dist = 0.20 # m

### Get tools
birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

for fullpath in full_filepath:
    image = cv2.imread(fullpath)

    lane_image = np.copy(image)

    binary, color, sobel, skyview, curve_fit_result = process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter)

    # Show image
    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    # cv2.imshow('color', color)
    # cv2.imshow('sobel', sobel)
    cv2.imshow('curve fit result', curve_fit_result['image'])

    if cv2.waitKey(1000) == 'q':
        continue

cv2.destroyAllWindows()