'''
实验名称：串口通信
版本：v1.0
作者：WalnutPi
实验平台：核桃派PicoW
说明：通过编程实现串口通信，跟电脑串口助手实现数据收发。
'''

#导入串口模块
from machine import UART

uart=UART(1,115200,rx=42,tx=41) #设置串口号1和波特率

uart.write('Hello 01Studio!')#发送一条数据

while True:

    #判断有无收到信息
    if uart.any():

        text=uart.read(128) #接收128个字符        

        # 将字节串解码为字符串
        decoded_data = text.decode('ascii')

        # 使用 split 方法分割字符串
        values = decoded_data.split(',')

        # 解析各个值
        center_l = int(values[0].strip())  # 转换为整数并去除空格
        center_h = int(values[1].strip())  # 转换为整数并去除空格
        angle = float(values[2].strip())  # 转换为浮点数并去除空格

