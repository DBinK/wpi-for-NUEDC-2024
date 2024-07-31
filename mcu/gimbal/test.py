'''
实验名称：串口通信
版本：v1.0
作者：WalnutPi
实验平台：核桃派PicoW
说明：通过编程实现串口通信，跟电脑串口助手实现数据收发。
'''

#导入串口模块
from machine import UART, Pin, SoftI2C
import mpu6050,time,math


uart=UART(1,115200,rx=42,tx=41) #设置串口号1和波特率

uart.write('Hello 01Studio!')#发送一条数据

LED=Pin(4,Pin.OUT) #构建led对象，GPIO46,输出
LED.value(1) #点亮LED，也可以使用led.on()

time.sleep(1)
    
#构建I2C对象
i2c1 = SoftI2C(scl=Pin(2), sda=Pin(1))

#构建MPU6050对象
mpu  = mpu6050.accel(i2c1)

fix_yaw_offset = 0 
yaw = 0
dt = 0

while True:

    start_time = time.time()
    
    gyro = mpu.get_values()['GyX'], mpu.get_values()['GyY'], mpu.get_values()['GyZ']
        
    yaw += gyro[2] * dt * 0.001 - fix_yaw_offset #! 零漂误差参数
    yaw_deg = yaw * 180 / math.pi
    
    #打印六轴加速度计原始值
    # print(mpu.get_values())
    print(yaw_deg)
    

    # time.sleep(0.02)

    #判断有无收到信息
    if uart.any():

        text=uart.read(128) #接收128个字符
        print(text) #通过REPL打印串口3接收的数据
    
    time.sleep(0.02)
    
    end_time = time.time()
    dt = end_time - start_time
    