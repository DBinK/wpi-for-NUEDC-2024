from machine import SoftI2C, Pin
import time
import math

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

class MPU6050:

    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))
        self.iic.stop()

        self.kalmanX = KalmanFilter()
        self.kalmanY = KalmanFilter()
        self.kalmanZ = KalmanFilter()

    def get_raw_values(self):
        self.iic.start()
        a = self.iic.readfrom_mem(self.addr, 0x3B, 14)
        self.iic.stop()
        return a

    def get_ints(self):
        b = self.get_raw_values()
        c = []
        for i in b:
            c.append(i)
        return c

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
        return vals  # returned in range of Int16
        # -32768 to 32767

    def get_angles(self):
        acc_x = self.mpu.get_values()['AcX']
        acc_y = self.mpu.get_values()['AcY']
        acc_z = self.mpu.get_values()['AcZ']
        gyro_x = self.mpu.get_values()['GyX'] / 131.0
        gyro_y = self.mpu.get_values()['GyY'] / 131.0
        gyro_z = self.mpu.get_values()['GyZ'] / 131.0  # 读取Z轴陀螺仪数据

        roll = math.atan2(acc_y, acc_z) * 180 / math.pi
        pitch = math.atan(-acc_x / math.sqrt(acc_y**2 + acc_z**2)) * 180 / math.pi

        dt = 0.01  # 假设每次调用间隔为10ms
        kalman_roll = self.kalmanX.get_angle(roll, gyro_x, dt)
        kalman_pitch = self.kalmanY.get_angle(pitch, gyro_y, dt)

        # 计算yaw角
        yaw = math.atan2(acc_y, acc_x) * 180 / math.pi  # 使用加速度计计算初始yaw
        kalman_yaw = self.kalmanZ.get_angle(yaw, gyro_z, dt)

        return kalman_roll, kalman_pitch, kalman_yaw


if __name__ == '__main__':
    
    VCC = Pin(3,Pin.OUT,value=1) 
    GND = Pin(2,Pin.OUT,value=0) 

    time.sleep(1)

    # 使用示例
    i2c = SoftI2C(scl=Pin(1), sda=Pin(0))  # 根据实际引脚配置
    mpu = MPU6050(i2c)

    while True:
        roll, pitch, yaw = mpu.get_angles()
        print("Roll: {:.2f}, Pitch: {:.2f}, Yaw: {:.2f}".format(roll, pitch, yaw))
        time.sleep(0.01)  # 每10ms读取一次