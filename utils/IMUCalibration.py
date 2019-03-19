import numpy as np
import time
from sensors.IMU import IMU

class IMUCalibration:
    def __init__(self, IMU):
        self._readings = []
        self._IMU = IMU
    
    def calibrate(self, iterations, sleep_seconds=0):
        for i in range(iterations):
            self._IMU.tick()
            self._readings.append(self._IMU.get_reading())
            if sleep != 0:
                time.sleep(sleep_seconds)
        
        means = {}
        for k in r.keys():
            means[k] = np.mean([r[k] for r in self._readings])
