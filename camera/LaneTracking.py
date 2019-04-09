import cv2
import numpy as np


def make_coordinates(image, line_parameters):
    try:
        slope, intercept = line_parameters
        y1 = image.shape[0]
        y2 = int(y1*3/5)
        x1 = int((y1 - intercept)/slope)
        x2 = int((y2 - intercept)/slope)
        return np.array([x1, y1, x2, y2])
    except:
        return np.array([None, None, None, None])

def levels_transform(gray_image):
    # make a transformation to flatten the image colors except for the brightest pixels
    return np.multiply(np.power(gray_image, 6, dtype='int64'), .0000000000009).astype('uint8')

def average_slope_intercept(image, lines):
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        slope = parameters[0]
        intercept = parameters[1]
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)
    left_line = make_coordinates(image, left_fit_average)
    right_line = make_coordinates(image, right_fit_average)

    output = []
    if all(left_line):
        output.append(left_line)
    if all(right_line):
        output.append(right_line)

    return np.array(output)

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

def process_one_frame(image, low_light_gradient_threshold, high_light_gradient_threshold, horizon, threshold_intersection, minLineLength, maxLineGap):
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

    try:
        # averaged_lines = average_slope_intercept(lane_image, lines)
        line_image = display_lines(lane_image, lines)
        # averaged_line_image = display_lines(line_image, averaged_lines, color=(255, 0, 255))

        # Overlay the images
        combo_image2 = cv2.addWeighted(lane_image, 0.8, line_image, 1, 1)
        # combo_image2 = cv2.addWeighted(combo_image1, 0.8, averaged_line_image, 1, 1)
    except:
        combo_image2 = lane_image

    return combo_image2, im_crop


### Get device
device = cv2.VideoCapture(0)

### Tuning parameters
low_light_gradient_threshold = 100
high_light_gradient_threshold = 150
horizon = 115
threshold_intersection = 5
minLineLength = 50
maxLineGap = 40

while True:
    print('start')
    ret, image = device.read()

    lane_image = np.copy(image)


    output_image, canny_image = process_one_frame(image, low_light_gradient_threshold, high_light_gradient_threshold,
                                                  horizon, threshold_intersection, minLineLength, maxLineGap)

    # show image
    cv2.imshow('result', output_image)
    if cv2.waitKey(100) == 'q':
        break

device.release()
cv2.destroyAllWindows()
