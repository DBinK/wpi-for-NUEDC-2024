import machine
from machine import SoftI2C, Pin
import math
import time

class KalmanFilter:
    def __init__(self):
        self.angle = 0.0
        self.bias = 0.0
        self.rate = 0.0
        self.P = 0.0
        self.Q = 0.001  # 过程噪声
        self.R = 0.003  # 量测噪声

    def get_angle(self, new_angle, new_rate, dt):
        self.rate = new_rate + self.bias
        self.angle += self.rate * dt

        self.P += self.Q
        S = self.P + self.R
        K = self.P / S
        self.angle += K * (new_angle - self.angle)
        self.P -= K * self.P

        return self.angle

class Accel:
    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))  # 唤醒 MPU6050
        self.iic.stop()
        
        # 初始化卡尔曼滤波器
        self.kalmanX = KalmanFilter()
        self.kalmanY = KalmanFilter()
        self.kalmanZ = KalmanFilter()

    def get_raw_values(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        self.iic.stop()
        return a

    def bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self):
        raw_ints = self.get_raw_values()
        vals = {}
        vals["AcX"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        vals["AcY"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        vals["AcZ"] = self.bytes_toint(raw_ints[4], raw_ints[5])
        vals["Tmp"] = self.bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        vals["GyX"] = self.bytes_toint(raw_ints[8], raw_ints[9])
        vals["GyY"] = self.bytes_toint(raw_ints[10], raw_ints[11])
        vals["GyZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])
        return vals  # 返回原始值

    def get_angles(self):
        vals = self.get_values()
        acc_x = vals["AcX"]
        acc_y = vals["AcY"]
        acc_z = vals["AcZ"]
        gyro_x = vals["GyX"] / 131.0
        gyro_y = vals["GyY"] / 131.0
        gyro_z = vals["GyZ"] / 131.0

        # 计算roll
        if acc_z != 0:  # 防止除以零
            roll = math.atan2(acc_y, acc_z) * 180 / math.pi
        else:
            roll = 0  # 或者设置为其他默认值

        # 计算pitch
        if acc_y**2 + acc_z**2 != 0:  # 防止除以零
            pitch = math.atan(-acc_x / math.sqrt(acc_y**2 + acc_z**2)) * 180 / math.pi
        else:
            pitch = 0  # 或者设置为其他默认值

        dt = 0.01  # 假设每次调用间隔为10ms
        kalman_roll = self.kalmanX.get_angle(roll, gyro_x, dt)
        kalman_pitch = self.kalmanY.get_angle(pitch, gyro_y, dt)

        # 计算yaw
        if acc_x != 0:  # 防止除以零
            yaw = math.atan2(acc_y, acc_x) * 180 / math.pi
        else:
            yaw = 0  # 或者设置为其他默认值

        kalman_yaw = self.kalmanZ.get_angle(yaw, gyro_z, dt)

        return kalman_roll, kalman_pitch, kalman_yaw

    def val_test(self):  # 仅用于测试
        while True:
            roll, pitch, yaw = self.get_angles()
            print("Roll: {:.2f}, Pitch: {:.2f}, Yaw: {:.2f}".format(roll, pitch, yaw))
            time.sleep(0.05)

if __name__ == "__main__":


    VCC = Pin(3,Pin.OUT,value=1) 
    GND = Pin(2,Pin.OUT,value=0) 

    time.sleep(1)

    from time import sleep
    i2c = machine.SoftI2C(scl=machine.Pin(1), sda=machine.Pin(0))
    mpu = Accel(i2c)
    while True:
        roll, pitch, yaw = mpu.get_angles()
        print("Roll: {:.2f}, Pitch: {:.2f}, Yaw: {:.2f}".format(roll, pitch, yaw))
        sleep(0.05)