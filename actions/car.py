# defines the class to control the car

from actions.car_connect import CarConnect
import camera.LaneTracking as LaneTracking
import cv2
from simple_pid import PID
from PyQt5.QtGui import QImage
import numpy as np
import time

# picar server info
HOST = '192.168.2.2'
Theoretical_lane_width = 30

def QImageToMat(qimg):
    """RGB888"""
    #qimg = QImage()
    #qimg.load("/home/auss/Pictures/test.png")
    qimg = qimg.convertToFormat(QImage.Format_RGB888)
    qimg = qimg.rgbSwapped()
    #assert(qimg.byteCount() == qimg.width() * qimg.height() * 3)

    ptr = qimg.constBits()

    if not ptr:
        return

    ptr.setsize(qimg.byteCount())

    mat = np.array(ptr).reshape( qimg.height(), qimg.width(), 3)  #  Copies the data
    return mat


class Car:
    def __init__(self, look_ahead_distance, speed, turning_coef):
        self.use_local_image = False
        self.car_connection = CarConnect(HOST, in_port=8080, out_port=8000)
        self.look_ahead_distance = look_ahead_distance
        self.speed = speed
        self.turning_coef = turning_coef

        self.birds_eye_obj, self.gradient_color_threshold_obj, self.curve_fitter_obj = LaneTracking.setupToolClasses()
        self.test_image = None

    def connect(self):
        self.car_connection.connection_ok()

    def get_image(self, index=0):
        if self.use_local_image:
            self.test_image = None
            time.sleep(1)
            return True
        else:
            if self.car_connection.is_connected:
                return self.car_connection.query_image()

            else:
                print("Connection to the car non existant... attempting connection")
                self.connect()
        return False

    def drive(self):
        steering_turn = 0
        while True:

            if self.get_image():
                q_image = QImage()

                if self.use_local_image:
                    q_image.load("../images/test_image.jpg")
                else :
                    q_image.loadFromData(self.car_connection.image)
                image = QImageToMat(q_image)

                binary, color, sobel, skyview, curve_fit_result = \
                    LaneTracking.process_one_frame(image,
                                                   self.birds_eye_obj,
                                                   self.gradient_color_threshold_obj,
                                                   self.curve_fitter_obj)

            # Calc steering based on look ahead distance ****** does not take into account of lost lane tracking
            x = self.look_ahead_distance

            fl = curve_fit_result['real_left_best_fit_curve']
            fr = curve_fit_result['real_right_best_fit_curve']
            # yl = fl[0] * x ** 3 + fl[1] * x ** 2 + fl[2] * x + fl[3]
            # yr = fr[0] * x ** 3 + fr[1] * x ** 2 + fr[2] * x + fr[3]

            if fl is None and fr is None:
                continue

            if fl is None:
                yl = fr[0] * x ** 2 + fr[1] * x + fr[2] - Theoretical_lane_width
            else:
                yl = fl[0] * x ** 2 + fl[1] * x + fl[2]

            if fr is None:
                yr = fl[0] * x ** 2 + fl[1] * x + fl[2] + Theoretical_lane_width
            else:
                yr = fr[0] * x ** 2 + fr[1] * x + fr[2]

            y_mid_ahead = (yl + yr) / 2 - self.curve_fitter_obj.w / 2 * self.curve_fitter_obj.kx  # wrt the car's center

            #####
            if yl != yr:
                pid = PID(40, 0.5, 0.1, setpoint=0)
                steering_turn = self.turning_coef * pid(y_mid_ahead)

                # # for higher velocity
                # if steering_turn > 1.5 or steering_turn <-1.5:
                #     run_speed(30)
                # else:
                #     run_speed(velocityPercentage)

            print(steering_turn + 90)
            #self.car_connection.run_action('fwturn:' + str(int(steering_turn + 90)))

            #####
            # cum_center_error += y_mid_ahead*timestep/1000
            # k = 400
            # steer_from_mid = k*cum_center_error
            # print(y_mid_ahead, cum_center_error)
            # run_action('fwturn:' + str(int(steer_from_mid+90)))

            # Show image
            cv2.imshow('result', skyview)
            # cv2.imshow('binary', binary)
            # cv2.imshow('color', color)
            # cv2.imshow('sobel', sobel)
            cv2.imshow('curve fit result', curve_fit_result['image'])
            # delta_time = t2 - t1
            # lapse_time = delta_time.seconds * 1000 + delta_time.microseconds/ 1000 # in mss
            # print(math.ceil(lapse_time))
            if cv2.waitKey(1) == 27:
                continue


if __name__ == '__main__':
    car = Car(15, 30, -2)
    car.use_local_image = True
    car.drive()
