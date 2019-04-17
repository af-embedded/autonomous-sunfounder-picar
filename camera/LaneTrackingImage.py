import cv2
import numpy as np
import os
from camera.LaneTracking import process_one_frame

# load image
this_file_path = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(this_file_path, 'SkyviewImages')
image_files = os.listdir(folder)

for filename in image_files:
    image = cv2.imread(os.path.join(folder, filename))

    lane_image = np.copy(image)

    output_image = process_one_frame(image)

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(100000) == 'q':
        continue