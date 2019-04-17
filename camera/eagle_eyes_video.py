# converting video to skyview

import numpy as np
from camera.birdseye import BirdsEye
import cv2
import matplotlib.pyplot as plt
import glob

# source_points = [(580, 460), (205, 720), (1110, 720), (703, 460)]
# destination_points = [(320, 0), (320, 720), (960, 720), (960, 0)]

source_points = [(25, 310), (251,75),  (608, 287), (379, 74)]
# destination_points = [(150, 450), (150, 100), (490, 450), (490, 100)]
destination_points = [(250, 450), (250, 100), (350, 450), (350, 100)]

# loading camera calibration parameters
camera_calibration_parameters = np.load('camera_calibration_parameters.npz')
camera_calibration_matrix = camera_calibration_parameters['camera_matrix']
distortion_coefficient = camera_calibration_parameters['distortion_coefficient']
birdsEye = BirdsEye(source_points, destination_points,
                    camera_calibration_matrix, distortion_coefficient)


# fname = "C:\\Users\\A550651\\Desktop\\TrackImages\\image21.jpg"
# fname = "C:\\Users\\A550651\\Desktop\\CalibrationImage\\calibrate.jpg"
counter = 1
# images = glob.glob('C:/Users/A550651/Desktop/curve_track_images/*.jpg')
cam = cv2.VideoCapture("C:\\Users\\A550651\\Desktop\\picar_video\\video_2019_04_16_11_12_17p869919.avi")

while True:
    ret, frame = cam.read()
    if ret:
        # raw_image = cv2.imread(frame)
        undistorted_image = birdsEye.undistort(frame)
        sky_view_image = birdsEye.sky_view(frame)
        # cv2.imshow('raw image ', raw_image)
        cv2.imshow('sky view', sky_view_image)
        # cv2.imshow('img', img)
        cv2.waitKey(100)
        # filename = "C:/Users/A550651/Desktop/SkyviewImages_curves/image%d.jpg" % counter
        # cv2.imwrite(filename, sky_view_image)
        # counter += 1
a =1
