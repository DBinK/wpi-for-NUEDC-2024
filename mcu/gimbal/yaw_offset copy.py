from machine import SoftI2C, Pin, UART
import mpu6050
import time
import math
from filter import window_filter, KalmanAngle

# 常量定义
GYRO_SENSI = 250 / 32768  # 陀螺仪灵敏度

# 创建 KalmanAngle 实例
kalman_filter = KalmanAngle()

# 设置初始角度（假设为0度）
kalman_filter.setAngle(0)

class MPU6050Controller:
    def __init__(self, scl_pin, sda_pin, dt=0.02):

        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.mpu = mpu6050.accel(self.i2c)

        self.dt = dt
        self.yaw = 0
        self.yaw_last = 0
        self.yaw_offset = 0

        self.cnt = 0

        self.dt2 = 0.02

    def test_gyro_offset(self, times=100):
        """
        测试零漂误差参数
        """
        real_gyros = []
        cnt = 1

        while cnt < times:

            gyro = self.mpu.get_values()['GyX'], self.mpu.get_values()['GyY'], self.mpu.get_values()['GyZ']
            real_gyro = gyro[2]  # * GYRO_SENSI

            real_gyro_avg = window_filter(real_gyro, real_gyros, cnt)

            print(f"gyro: {real_gyro}, avg: {real_gyro_avg}, cnt: {cnt}")

            cnt += 1

            time.sleep(0.005)

        print(f"零漂是{real_gyro_avg}")

        return real_gyro_avg

    def update(self):
        
        real_gyro_avg = self.test_gyro_offset(1000)
        
        uart = UART(1, 115200, rx=21, tx=20)
        uart.write('Hello MPU6050!\n')
        
        real_gyro_last = 0

        while True:
            st = time.ticks_us()

            gyro = self.mpu.get_values()['GyX'], self.mpu.get_values()['GyY'], self.mpu.get_values()['GyZ']

            real_gyro = (gyro[2] - real_gyro_avg) * GYRO_SENSI
            
            real_gyro_offset = real_gyro - real_gyro_last
            newRate = real_gyro_offset / self.dt2
        
            real_gyro_filted = kalman_filter.getAngle(real_gyro, newRate, self.dt2)

            self.yaw += real_gyro_filted * self.dt2

            # self.yaw_offset = self.yaw - self.yaw_last

            #newRate = self.yaw_offset / self.dt2
            #self.yaw_filted = kalman_filter.getAngle(self.yaw, newRate, self.dt2)
            self.yaw_filted = 0

            self.cnt += 1

            print_msg = f"yaw: {self.yaw}, cnt: {self.cnt}, delay: {self.dt2}\n"
            # print(print_msg)
            
            uart_msg = f"{self.yaw_filted},{self.yaw},{self.cnt},{self.dt2},{real_gyro},{real_gyro_filted}\n"
            uart.write(uart_msg)

            self.yaw_last = self.yaw
            
            real_gyro_last = real_gyro

            # time.sleep(0.001)

            et = time.ticks_us()

            self.dt2 = (et - st) / 1000000

# 主程序入口
if __name__ == "__main__":
    VCC = Pin(3, Pin.OUT, value=1)
    GND = Pin(2, Pin.OUT, value=0)

    time.sleep(2)

    controller = MPU6050Controller(scl_pin=1, sda_pin=0)

    controller.update()