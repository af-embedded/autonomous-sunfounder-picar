#!/usr/bin/env python
import math
import numpy as np
import matplotlib.pyplot as plt


class BezierSplineCreator(object):
    """ A class for creating Bezier splines.

    Nice illustration of Bezier curves: https://javascript.info/bezier-curve
    """

    def __init__(self, nbr_of_ctrl_points=4, D1_factor=4, D2_factor=2):
        """ Constructor for BezierSplineCreator

        Args:
            nbr_of_ctrl_points  (int): How many control points to use.
                                       The "order" of the Bezier curve.
            D1_factor           (int): The factor of the "look ahead" D1.
                                       I.e. D1 = 1 / D1_factor
            D2_factor           (int): The factor of the "look ahead" D2.
                                       I.e. D2 = 1 / D2_factor
        """
        self.nbr_of_ctrl_points = nbr_of_ctrl_points
        self.D1_factor = D1_factor
        self.D2_factor = D2_factor

    def bezier_formula_4P(self, time, point_1, point_2, point_3, point_4):
        """ Implements the Bezier formula using 4 points for one time instance
        To avoid using matrix operations the x- and y-points are calculated separately.
        The Bezier formula: P = (1−t)^3*P1 + 3(1−t)^2t*P2 +3(1−t)t^2*P3 + t^3*P4

        Args:
            time         (float): Time to calculate the equation at.
            point_1 (ndarray[2]): The first point used in the Bezier formula.
            point_2 (ndarray[2]): The second point used in the Bezier formula.
            point_3 (ndarray[2]): The third point used in the Bezier formula.
            point_4 (ndarray[2]): The forth point used in the Bezier formula.

        Returns:
            points (list): x and y coordinate for the calculated spline at time t.

        """
        x = (np.power(1 - time, 3)) * point_1[0] + 3 * (np.power(1 - time, 2)) * time * point_2[0] + \
            3 * (1 - time) * np.power(time, 2) * \
            point_3[0] + np.power(time, 3) * point_4[0]
        y = (np.power(1 - time, 3)) * point_1[1] + 3 * (np.power(1 - time, 2)) * time * point_2[1] + \
            3 * (1 - time) * np.power(time, 2) * \
            point_3[1] + np.power(time, 3) * point_4[1]
        return [x, y]

    def get_bezier_spline_points(self, nbr_of_points, point_1, point_2, point_3, point_4):
        """ Uses the Bezier formula and returns a list of points on the spline.

        Args:
            nbr_of_points  (int): The desired number of points in the result.
            point_1 (ndarray[2]): The first point used in the Bezier formula.
            point_2 (ndarray[2]): The second point used in the Bezier formula.
            point_3 (ndarray[2]): The third point used in the Bezier formula.
            point_4 (ndarray[2]): The forth point used in the Bezier formula.

        Returns:
            points (list): List of ndarrays of points on the Bezier spline.
        """

        time_vector = np.linspace(0.0, 1.0, num=nbr_of_points)
        points = [self.bezier_formula_4P(
            time, point_1, point_2, point_3, point_4) for time in time_vector]
        return points

    def get_bezier_spline_point_angle(self, nbr_of_points, target_point, target_angle=0):
        """ Uses the Bezier formula and returns a list of points on the spline.
            D1 and D2 used for calculating points are a sort of "look ahead distance"
            and can be used as tuning parameters.

        Args:
            nbr_of_points     (int): The desired number of points in the result.
            target_point (ndarray[2]): The target point relative to the current position.
            target_angle        (int): The target angle relative to the current angle.
                                     Positive - left, negative - right.
                                     If not given, the angle is assumed to be the same
                                     as the current.

        Returns:
            points (list): List of ndarrays of points on the Bezier spline.
        """
        target_angle_rad = math.radians(target_angle)
        D1 = target_point[0] / float(self.D1_factor)
        D2 = target_point[0] / float(self.D2_factor)
        P1 = np.array([0., 0.])
        P2 = np.array([D1, 0.])
        P3 = target_point - \
            np.array([D2 * math.cos(target_angle_rad),
                      D2 * math.sin(target_angle_rad)])
        P4 = target_point
        time_vector = np.linspace(0.0, 1.0, num=nbr_of_points)
        points = [self.bezier_formula_4P(
            time, P1, P2, P3, P4) for time in time_vector]
        return points

    def plot_example_curves(self):
        """ Example for calculating three splines and plotting them
        """
        target_points = [np.array([4., 2., 45]), 
                         np.array([4., 0., -15]), 
                         np.array([4., -2., 45])]

        for point in target_points:
            b_spline_points = self.get_bezier_spline_point_angle(
                50, point[:-1], point[-1])
            x_values = [point[0] for point in b_spline_points]
            y_values = [point[1] for point in b_spline_points]

            plt.plot(x_values, y_values)
            plt.plot(point[0], point[1], 'go')
            plt.annotate(str(point), xy=(point[0], point[1]), xytext=(
                point[0] - 0.4, point[1] + 0.1))

        plt.title('Example of B-splines')
        plt.ylabel('y [m]')
        plt.xlabel('x [m]')
        plt.plot(0.0, 0.0, 'ro')
        plt.show()
