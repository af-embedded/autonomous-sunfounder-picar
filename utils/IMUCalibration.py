import numpy as np
import time
from sensors.IMU import IMU

class IMUCalibration:
    def __init__(self):
	"""
		IMU Calibration class
		Originally written for MPU-9250 9-DOF IMU Sensor
		
		This class calibrates the IMU by taking a sequence of
		readings and calculating the mean of the readings.
		The mean readings are then passed to the IMU for calibration.
		
		Before calibrating the IMU, make sure that the IMU is fitted
		properly and is at rest. If the orientation of the IMU is changed
		then it will need to be recalibrated
	"""
        self._readings = []
    
    def calibrate(self, imu, iterations, sleep_seconds=0):
	"""
		Calibrate the given IMU.
		The IMU must be fitted properly and should be stationary
		in its rest position
		
		:param imu: The IMU object
		:param iterations: The number of readings to take
		:param sleep_seconds: Delay between each reading
	"""
        for i in range(iterations):
            imu.tick()
            self._readings.append(imu.get_reading())
            if sleep_seconds != 0:
                time.sleep(sleep_seconds)
        
        means = {}
        for k in self._readings[0].keys():
            means[k] = np.mean([r[k] for r in self._readings])

        imu.set_calibration(means)
