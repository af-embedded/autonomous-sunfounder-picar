import cv2
import numpy as np
import math

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

def process_one_frame(image):
    ### Tuning parameters
    low_light_gradient_threshold = 100
    high_light_gradient_threshold = 150
    horizon = 150
    threshold_intersection = 5
    minLineLength = 50
    maxLineGap = 40

    lane_image = np.copy(image)

    # convert to gray scale
    im_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # blur the image
    im_blur = cv2.GaussianBlur(im_gray, (17, 17), 0)

    # levels transformation
    im_levelled = levels_transform(im_blur)

    # canny function takes the derivative to calculate the gradient
    im_canny = cv2.Canny(im_levelled, low_light_gradient_threshold, high_light_gradient_threshold)

    # crop
    im_crop = region_of_interest(im_canny, horizon)

    # Hough space best fit line
    lines = cv2.HoughLinesP(im_crop, 2, np.pi / 180, threshold_intersection, np.array([]), minLineLength=minLineLength,
                            maxLineGap=maxLineGap)

    averaged_lines, averaged_line = average_slope_intercept(lane_image, lines)
    line_image = display_lines(lane_image, lines)
    averaged_lines_image = display_lines(line_image, averaged_lines, color=(255, 0, 255))
    hasAveragedLine = type(averaged_line) == np.ndarray or averaged_line != None
    if hasAveragedLine:
        averaged_line_image = display_lines(line_image, [averaged_line], color=(255, 255, 0))

    # Overlay the images
    combo_image1 = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)
    combo_image2 = cv2.addWeighted(combo_image1, 0.8, averaged_lines_image, 1, 1)
    if hasAveragedLine:
        combo_image2 = cv2.addWeighted(combo_image2, 0.8, averaged_line_image, 1, 1)

    return combo_image2, im_crop, averaged_lines, averaged_line

def convert_theta_r_to_m_b(t, r):
    m = -math.cos(t) / math.sin(t)
    b = r / math.sin(t)
    return m, b

if __name__ == '__main__':
    ### Get device
    device = cv2.VideoCapture(0)

    while True:
        ret, image = device.read()

        lane_image = np.copy(image)


        output_image, canny_image, averaged_lines, averaged_line = process_one_frame(image)

        try:
            x1, y1, x2, y2 = averaged_line
            print((y2-y1)/(x2-x1))
        except:
            print('no averaged line')

        # show image
        cv2.imshow('result', output_image)
        if cv2.waitKey(100) == 'q':
            break

    device.release()
    cv2.destroyAllWindows()
