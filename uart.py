'''
实验名称：UART(串口通讯)
实验平台：核桃派
'''

#导入相关模块
import serial,time

class Uart():
    def __init__(self,device="/dev/ttyUSB0",baud=115200):
        self.com = serial.Serial(device, baud)

    def send(self,data):
        self.com.write(data)

