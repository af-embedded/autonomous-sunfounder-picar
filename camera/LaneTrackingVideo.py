import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame
import matplotlib.pyplot as plt
import math

# load video
filename = 'video_2019_04_16_11_12_17p869919.avi'
this_file_path = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(this_file_path, 'test_videos', filename)
vidcap = cv2.VideoCapture(video_path)

timestep = 100 # ms

frame_counter = 0
while True:
    frame_counter += 1
    vidcap.set(cv2.CAP_PROP_POS_MSEC, frame_counter * timestep)
    hasFrames, image = vidcap.read()
    if not hasFrames:
        break

    lane_image = np.copy(image)

    # output_image, canny_image, averaged_lines, averaged_line = process_one_frame(image)
    output_image = process_one_frame(image)

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(timestep) == 'q':
        continue