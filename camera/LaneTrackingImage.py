import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame, setupToolClasses

# load image
# this_file_path = os.path.dirname(os.path.abspath(__file__))
# folder = os.path.join(this_file_path, 'SkyviewImages')
# image_files = os.listdir(folder)
image_files = ['C:\\Work\\autonomous-sunfounder-picar\\camera\\test_image.jpg']

### Get tools
birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

for filename in image_files:
    # image = cv2.imread(os.path.join(folder, filename))
    image = cv2.imread(filename)

    lane_image = np.copy(image)

    binary, color, sobel, skyview = process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter)

    # Show image

    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    cv2.imshow('color', color)
    cv2.imshow('sobel', sobel)
    if cv2.waitKey(100000) == 'q':
        continue