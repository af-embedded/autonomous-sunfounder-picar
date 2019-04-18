import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame, setupToolClasses


# load video
filename = 'video_2019_04_16_11_12_17p869919.avi'
video_path = os.path.join('C:\\Users\\horac\\OneDrive - AF', 'test_videos', filename)
vidcap = cv2.VideoCapture(video_path)

look_ahead_dist = 0.40 # m

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

    binary, color, sobel, skyview, curve_fit_result = \
        process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter,
                          image_folder_path='C:\\Users\\horac\\OneDrive - AF\\poor_performance_images')

    # Calc steering based on look ahead distance
    x = look_ahead_dist
    fl = curve_fit_result['real_left_best_fit_curve']
    fr = curve_fit_result['real_right_best_fit_curve']
    yl = fl[0] * x ** 3 + fl[1] * x ** 2 + fl[2] * x + fl[3]
    yr = fr[0] * x ** 3 + fr[1] * x ** 2 + fr[2] * x + fr[3]
    y_mid_ahead = (yl + yr) / 2 - curveFitter.w / 2 * curveFitter.kx  # wrt the car's center

    # Show image
    cv2.imshow('result', skyview)
    cv2.imshow('binary', binary)
    # cv2.imshow('color', color)
    # cv2.imshow('sobel', sobel)
    cv2.imshow('curve fit result', curve_fit_result['image'])

    if cv2.waitKey(timestep) == 'q':
        continue

cv2.destroyAllWindows()