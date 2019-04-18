import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame, setupToolClasses


# load video
filename = 'video_2019_04_16_11_12_17p869919.avi'
video_path = os.path.join('C:\\Users\\A551221\\OneDrive - AF', 'test_videos', filename)
vidcap = cv2.VideoCapture(video_path)

timestep = 100 # ms


### Get tools
birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

frame_counter = 0
while True:
    frame_counter += 1
    vidcap.set(cv2.CAP_PROP_POS_MSEC, frame_counter * timestep)
    hasFrames, image = vidcap.read()
    if not hasFrames:
        break

    lane_image = np.copy(image)

    binary, color, sobel, skyview = process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter)

    # Show image

    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    cv2.imshow('color', color)
    cv2.imshow('sobel', sobel)
    if cv2.waitKey(timestep) == 'q':
        continue