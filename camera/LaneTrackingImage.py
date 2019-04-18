import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame, setupToolClasses

# load image
folder = os.path.join('C:\\Users\\A551221\\OneDrive - AF', 'track_images')
image_files = os.listdir(folder)
full_filepath = [os.path.join(folder, file) for file in image_files]

### Get tools
birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

for fullpath in full_filepath:
    image = cv2.imread(fullpath)

    lane_image = np.copy(image)

    binary, color, sobel, skyview = process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter)

    # Show image

    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    cv2.imshow('color', color)
    cv2.imshow('sobel', sobel)
    if cv2.waitKey(100) == 'q':
        continue