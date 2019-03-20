import numpy as np
import time
from sensors.IMU import IMU

class IMUCalibration:
    def __init__(self):
        self._readings = []
    
    def calibrate(self, imu, iterations, sleep_seconds=0):
        for i in range(iterations):
            imu.tick()
            self._readings.append(imu.get_reading())
            if sleep_seconds != 0:
                time.sleep(sleep_seconds)
        
        means = {}
        for k in self._readings[0].keys():
            means[k] = np.mean([r[k] for r in self._readings])

        imu.set_calibration(means)
        return means
