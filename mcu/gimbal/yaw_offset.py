from machine import SoftI2C, Pin, UART, Timer
import mpu6050
import time
import math
from filter import window_filter, KalmanAngle

# 创建 KalmanAngle 实例
kalman_filter = KalmanAngle()

# 设置初始角度（假设为0度）
kalman_filter.setAngle(90)

class MPU6050Controller:
    def __init__(self, scl_pin, sda_pin, 
                    uart_id   = 1, 
                    baud_rate = 115200, 
                    rx_pin    = 21, 
                    tx_pin    = 20, 
                    dt        = 0.02):

        self.i2c  = SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.mpu  = mpu6050.accel(self.i2c)
        self.uart = UART(uart_id, baud_rate, rx=rx_pin, tx=tx_pin)
        self.uart.write('Hello MPU6050!\n')
        
        self.dt = dt
        self.yaw = 0
        self.yaw_deg = 0
        self.yaw_last = 0
        self.yaw_offset = 0
        self.yaw_offset_values = []
        self.yaw_deg_values = []
        
        self.fix_yaw_offset = 0.002219471      # 0.002219471 无滤波
        
        self.cnt = 0
        self.test_time = 600
        
        self.dt2 = 0.02
        
        self.window_size = 1023 # self.test_time / self.dt2
        self.timer = None


    def test_yaw_offset(self):
        """
        测试零漂误差参数
        """
        pass

    def test(self):

        while True:

            st = time.ticks_us()

            gyro = self.mpu.get_values()['GyX'], self.mpu.get_values()['GyY'], self.mpu.get_values()['GyZ']
            
            self.yaw += gyro[2] * self.dt2 * 0.001 - self.fix_yaw_offset #! 零漂误差参数
            self.yaw_deg = self.yaw * 180 / math.pi
            
            self.yaw_offset = self.yaw - self.yaw_last
            
            
            avg_yaw_offset  = window_filter(self.yaw_offset, self.yaw_offset_values, self.window_size)
            
            newRate = self.yaw_offset / self.dt2
            # self.yaw_deg   = window_filter(self.yaw_deg, self.yaw_deg_values, 3)
            self.yaw_deg   = kalman_filter.getAngle(self.yaw, newRate, self.dt2)
            
            self.cnt += 1
            
            uart_msg = f"yaw: {self.yaw_deg}, offset: {avg_yaw_offset}, cnt: {self.cnt}, delay: {self.dt2}\n"
            self.uart.write(uart_msg)
            print(uart_msg)

            self.yaw_last   = self.yaw

            time.sleep(0.02)

            et = time.ticks_us()

            self.dt2 = (et - st)/1000000
            
#             if self.cnt > self.window_size:
#                 print(f"测试完成, avg_yaw_offset = {avg_yaw_offset}")
#                 break


if __name__ == "__main__":
    
    LED=Pin(4,Pin.OUT) #构建led对象，GPIO46,输出
    LED.value(1) #点亮LED，也可以使用led.on()

    time.sleep(2)
    
    controller = MPU6050Controller(0, 1)
    controller.test()