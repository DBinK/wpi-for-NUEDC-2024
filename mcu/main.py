"""
实验名称：串口通信
版本：v1.0
作者：WalnutPi
实验平台：核桃派PicoW
说明：通过编程实现串口通信，跟电脑串口助手实现数据收发。
"""
import time
from machine import UART, Pin # type: ignore

import motor

moto = motor.Motor()

uart = UART(1, 115200, rx=42, tx=41)  # 设置串口号1和波特率
KEY  = Pin(0,Pin.IN,Pin.PULL_UP) #构建KEY对象
LED  = Pin(46,Pin.OUT) #构建LED对象,开始熄灭

center_l = 0
center_h = -1
angle    = -1

line_follow = False

#LED状态翻转函数
def fun(KEY):
    global line_follow
    time.sleep_ms(10) #消除抖动
    if KEY.value()==0: #确认按键被按下
        line_follow = not line_follow
        LED.value(line_follow)

KEY.irq(fun,Pin.IRQ_FALLING) #定义中断，下降沿触发

uart.write("Hello 01Studio!")  # 发送一条数据
print("开始串口通信")

while True:

    # 判断有无收到信息
    if uart.any():
        text = uart.read(128)  # 接收128个字符
        decoded_data = text.decode("ascii")  # 将字节串解码为字符串
        
        print(decoded_data)
        
        values = decoded_data.split(",")     # 使用 split 方法分割字符串

        center_h = int(values[0].strip())    # 转换为整数并去除空格
        center_l = int(values[1].strip())    # 转换为整数并去除空格
        angle    = float(values[2].strip())  # 转换为浮点数并去除空格
        l_motor_sp  = int(values[3].strip())
        l_motor_sp  = int(values[4].strip()) 

    if line_follow:
        # moto.Motor_Control(center_h)
        # print(center_l)
        moto.l_motor(l_motor_sp)
        moto.r_motor(l_motor_sp)
        
    else:
        moto.stop()
        # print("pause follow")
    
    time.sleep(0.01)
