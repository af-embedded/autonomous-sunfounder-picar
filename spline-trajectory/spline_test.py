#!/usr/bin/env python
import math
import numpy as np
import matplotlib.pyplot as plt
import BezierSplineCreator

# Create a Bezier Spline Class
bspline4 = BezierSplineCreator.BezierSplineCreator(nbr_of_ctrl_points=4)

# Set some target points with angles
target_points = [np.array([4., 2., 45]), 
                 np.array([4., 0., -15]), 
                 np.array([4., -2., 45])]

# Get splines and plot for the points
for point in target_points:
    b_spline_points = bspline4.get_bezier_spline_point_angle(
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