from machine import SoftI2C, Pin, UART, Timer
import mpu6050
import time
import math
from filter import window_filter

class MPU6050Controller:
    def __init__(self, scl_pin, sda_pin, 
                    uart_id   = 1, 
                    baud_rate = 115200, 
                    rx_pin    = 12, 
                    tx_pin    = 11, 
                    dt        = 0.02):

        self.i2c = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.mpu = mpu6050.accel(self.i2c)
        self.uart = UART(uart_id, baud_rate, rx=rx_pin, tx=tx_pin)
        self.uart.write('Hello MPU6050!\n')
        
        self.dt = dt
        self.yaw = 0
        self.yaw_deg = 0
        self.yaw_last = 0
        self.yaw_offset = 0
        self.yaw_offset_values = []
        self.yaw_deg_values = []
        self.fix_yaw_offset = 0
        
        self.cnt = 0
        self.test_time = 5
        self.window_size = self.test_time / self.dt
        self.timer = None

    def test_yaw_offset(self):
        """
        测试零漂误差参数
        """
        pass

    def start_test(self):
        self.cnt = 0
        self.timer = Timer(1)
        self.timer.init(period=int(self.dt*1000), mode=Timer.PERIODIC, callback=self.test)
        print(f"Window size: {self.window_size}")

    def test(self, tim):
        gyro = self.mpu.get_values()['GyX'], self.mpu.get_values()['GyY'], self.mpu.get_values()['GyZ']
        
        self.yaw += gyro[2] * self.dt * 0.001 - self.fix_yaw_offset #! 零漂误差参数
        self.yaw_deg = self.yaw * 180 / math.pi
        
        self.yaw_offset = self.yaw - self.yaw_last
        self.yaw_last   = self.yaw
        avg_yaw_offset  = window_filter(self.yaw_offset, self.yaw_offset_values, self.window_size)
        
        self.yaw_deg   = window_filter(self.yaw_deg, self.yaw_deg_values, 10)
        
        self.cnt += 1
        uart_msg = f"test:0,0,{self.yaw_deg},{avg_yaw_offset},{self.cnt}\n"
        self.uart.write(uart_msg)
        
        if self.cnt > self.window_size:
            print(f"测试完成, avg_yaw_offset = {avg_yaw_offset}")
            self.timer.deinit()

if __name__ == "__main__":
    controller = MPU6050Controller(scl_pin = 2, sda_pin = 1)
    controller.start_test()