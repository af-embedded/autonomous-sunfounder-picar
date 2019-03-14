import math
from .MPU9250 import MPU9250

class IMU:
    def __init__(self, accel_shuffle='xyz', gyro_shuffle='xyz', magnet_shuffle='xyz'):
        """
        9-DOF Inertial Measurement Unit (IMU) sensor.

        :param accel_shuffle: The order of accelerometer readings
        :param gyro_shuffle: The order of gyroscope readings
        :param magnet_shuffle: The order of magnetometer readings
        """
        self._mpu9250 = MPU9250()
        self._accel_shuffle = accel_shuffle
        self._gyro_shuffle = gyro_shuffle
        self._magnet_shuffle = magnet_shuffle
        self._reading = {}
        self._g_force = 9.81
        self._deg_to_rad = math.pi / 180.0
        
    def tick(self):
        accel = self._mpu9250.readAccel()
        gyro = self._mpu9250.readGyro()
        mag = self._mpu9250.readMagnet()
        temp = self._mpu9250.readTemperature()
        
        accel = self._multiply_by(accel, self._g_force)
        gyro = self._multiply_by(gyro, self._deg_to_rad)
        
        accel = self._shuffle(accel, self._accel_shuffle)
        gyro = self._shuffle(gyro, self._gyro_shuffle)
        mag = self._shuffle(mag, self._magnet_shuffle)
        self._reading = {
            'ax': accel['x'],
            'ay': accel['y'],
            'az': accel['z'],
            'gx': gyro['x'],
            'gy': gyro['y'],
            'gz': gyro['z'],
            'mx': mag['x'],
            'my': mag['y'],
            'mz': mag['z'],
            'temp': temp
        }
        
    def get_reading(self):
        return self._reading
        
    def _shuffle(self, data, new_format='xyz'):
        output = {}
        axis = 'xyz'
        for i in range(3):
            output[new_format[i]] = data[axis[i]]
        return output
        
    def _multiply_by(self, data, factor):
        output = {}
        for k in data:
            output[k] = data[k] * factor
        return output