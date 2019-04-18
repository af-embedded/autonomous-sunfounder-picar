import cv2
import numpy as np
import math
from camera.gradientColorThreshold import GradientColorThreshold
from camera.curveFit import Curves
from camera.birdseye import BirdsEye
import os

def make_coordinates(image, line_parameters):
    try:
        slope, intercept = line_parameters
        y1 = image.shape[0]
        y2 = int(y1/5)
        x1 = int((y1 - intercept)/slope)
        x2 = int((y2 - intercept)/slope)
        return np.array([x1, y1, x2, y2])
    except:
        return None

def levels_transform(gray_image):
    # make a transformation to flatten the image colors except for the brightest pixels
    return np.multiply(np.power(gray_image, 6, dtype='int64'), .0000000000009).astype('uint8')


def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []

    try:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            intercept = parameters[1]
            if x1 < image.shape[1]/2 and x2 < image.shape[1]/2:
                left_fit.append((slope, intercept))
            elif x1 > image.shape[1]/2 and x2 > image.shape[1]/2:
                right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        right_fit_average = np.average(right_fit, axis=0)
        left_line = make_coordinates(image, left_fit_average)
        right_line = make_coordinates(image, right_fit_average)
    except:
        print('no lines')
        left_line = None
        right_line = None

    averaged_lines = []
    hasLeftLine = type(left_line) == np.ndarray or left_line != None
    hasRightLine = type(right_line) == np.ndarray or right_line != None
    if hasLeftLine:
        averaged_lines.append(left_line)
    if hasRightLine:
        averaged_lines.append(right_line)

    # average the left and right lanes
    if hasLeftLine and hasRightLine:
        averaged_line = np.average(averaged_lines, axis=0).astype('int')
    else:
        print('no lines found')
        averaged_line = None

    return averaged_lines, averaged_line

def region_of_interest(image, horizon):
    height = image.shape[0]
    width = image.shape[1]
    mask = np.zeros_like(image)

    # add white rectangle to black mask
    white_polygons = np.array([
        [[0, height], [width, height], [width, horizon], [0, horizon]]
    ])
    cv2.fillPoly(mask, white_polygons, 255)

    # add black rectangle for the shadow
    black_polygons = np.array([
        [[100, height], [width-100, height], [width-150, 300], [150, 300]]
    ])
    cv2.fillPoly(mask, black_polygons, 0)

    masked_image = cv2.bitwise_and(image, mask)

    return masked_image

def display_lines(image, lines, color=(0, 255, 0)):
    line_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(line_image, (x1, y1), (x2, y2), color, 2)
    return line_image

def firstNum(name):
    num = int(name[:-21])
    return num

def process_one_frame(lane_image, birdsEye, gradientColorThreshold, curveFitter):

    ### Bird View undistort
    im_skyview = birdsEye.sky_view(lane_image)

    ### Gradient and Color
    # - this does 2 things, color mask and sobel(gradient) mask
    # color mask masks the saturation and light values of the color
    # sobel mask masks the magnitude of the gradient, the x component of the gradient, and the angle of the gradient

    # color filter
    im_blur = cv2.GaussianBlur(im_skyview, (7, 7), 0)
    gradientColorThreshold.apply_hls(im_blur)
    b_color = gradientColorThreshold.apply_color_mask()

    # sobel filter
    im_gray = cv2.cvtColor(im_skyview, cv2.COLOR_RGB2GRAY)
    im_blur = cv2.GaussianBlur(im_gray, (17, 17), 0)
    im_levelled = levels_transform(im_blur)
    gradientColorThreshold.apply_l(im_levelled)
    b_sobel = gradientColorThreshold.apply_sobel_mask()

    b_filtered = cv2.bitwise_or(b_sobel, b_color)

    ### Curve fit
    curve_fit_result = curveFitter.fit(b_filtered)

    return b_filtered*255, b_color*255, b_sobel*255, im_skyview, curve_fit_result

def convert_theta_r_to_m_b(t, r):
    m = -math.cos(t) / math.sin(t)
    b = r / math.sin(t)
    return m, b

def setupToolClasses():

    ### BirdsEye
    d = 67.2 # cm
    w = 13.8 #cm
    d_dest = 350 #px
    w_dest = w/d*d_dest #px

    mid_px = 300
    max_y_px = 450

    # lower left, upper left, lower right, upper right
    source_points = [(25, 310), (251, 75), (608, 287), (379, 74)]
    destination_points = [
        (int(mid_px-w_dest/2), int(max_y_px)),
        (int(mid_px-w_dest/2), int(max_y_px-d_dest)),
        (int(mid_px+w_dest/2), int(max_y_px)),
        (int(mid_px+w_dest/2), int(max_y_px-d_dest))
    ]

    # loading camera calibration parameters
    this_file_dir = os.path.dirname(__file__)
    camera_calibration_parameters = np.load(os.path.join(this_file_dir, 'camera_calibration_parameters.npz'))
    camera_calibration_matrix = camera_calibration_parameters['camera_matrix']
    distortion_coefficient = camera_calibration_parameters['distortion_coefficient']
    birdsEye = BirdsEye(source_points, destination_points,
                        camera_calibration_matrix, distortion_coefficient)

    ### GradientColorThreshold
    p = {'sat_thresh': 80, 'light_thresh': 200, 'light_thresh_agr': 245,
         'grad_thresh': (0, 0.8), 'mag_thresh': 120, 'x_thresh': 100}
    gradientColorThreshold = GradientColorThreshold(p)

    ### Curves
    xm_per_pix = d/100/d_dest
    ym_per_pix = w/100/w_dest
    curveFitter = Curves(number_of_windows=9, margin=20, minimum_pixels=15,
                    ym_per_pix=ym_per_pix, xm_per_pix=xm_per_pix, poly_deg=3)

    return birdsEye, gradientColorThreshold, curveFitter

if __name__ == '__main__':
    ### Get tools
    birdsEye, gradientColorThreshold, curveFitter = setupToolClasses()

    ### Get device
    device = cv2.VideoCapture(0)

    while True:
        ret, image = device.read()

        lane_image = np.copy(image)

        output_image = process_one_frame(image, birdsEye, gradientColorThreshold, curveFitter)

        # show image
        cv2.imshow('result', output_image)
        if cv2.waitKey(100) == 'q':
            break

    device.release()
    cv2.destroyAllWindows()
