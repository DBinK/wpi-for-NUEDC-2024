from machine import SoftI2C, Pin, UART, Timer
import mpu6050
import time
import math
from filter import window_filter, KalmanAngle

GYRO_SENSI = 250/32768
RAG2DEG = 180/math.pi

# 创建 KalmanAngle 实例
kalman_filter = KalmanAngle()

# 设置初始角度（假设为0度）
kalman_filter.setAngle(0)

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


    def test_gyro_offset(self, times=100):
        """
        测试零漂误差参数
        """
        real_gyros = []
        cnt = 1

        while cnt < times:
            gyro = self.mpu.get_values()['GyX'], self.mpu.get_values()['GyY'], self.mpu.get_values()['GyZ']
            real_gyro = gyro[2] * GYRO_SENSI

            real_gyro_avg = window_filter(real_gyro, real_gyros, cnt)

            print(f"gyro: {real_gyro}, avg: {real_gyro_avg}, cnt: {cnt}")

            cnt += 1
            
            time.sleep(0.02)
        
        print(f"零漂是 :{real_gyro_avg}")
            
        return real_gyro_avg

    def test(self):
        
        real_gyro_avg = self.test_gyro_offset(200)
        
        # real_gyro_avg = 0

        while True:

            st = time.ticks_us()

            gyro = self.mpu.get_values()['GyX'], self.mpu.get_values()['GyY'], self.mpu.get_values()['GyZ']
            
            real_gyro = gyro[2] * GYRO_SENSI - real_gyro_avg #! 零漂误差参数
            
            self.yaw += real_gyro * self.dt2
            
            self.yaw_deg = self.yaw * RAG2DEG
            
            self.yaw_offset = self.yaw - self.yaw_last
            
            avg_yaw_offset  = window_filter(self.yaw_offset, self.yaw_offset_values, 50)
            
            newRate = self.yaw_offset / self.dt2
            # self.yaw_deg   = window_filter(self.yaw_deg, self.yaw_deg_values, 3)
            self.yaw_deg   = kalman_filter.getAngle(self.yaw, newRate, self.dt2)
            
            self.cnt += 1
            
            uart_msg = f"yaw: {self.yaw_deg}, offset: {avg_yaw_offset}, cnt: {self.cnt}, delay: {self.dt2}\n"
            self.uart.write(uart_msg)
            print(uart_msg)

            self.yaw_last = self.yaw

            time.sleep(0.02)

            et = time.ticks_us()

            self.dt2 = (et - st)/1000000
            
#             if self.cnt > self.window_size:
#                 print(f"测试完成, avg_yaw_offset = {avg_yaw_offset}")
#                 break


if __name__ == "__main__":
    
    VCC = Pin(3,Pin.OUT,value=1) 
    GND = Pin(2,Pin.OUT,value=0) 


    time.sleep(2)
    
    controller = MPU6050Controller(scl_pin=1,sda_pin=0)
    
    # controller.test_gyro_offset(1000)
    
    controller.test()
