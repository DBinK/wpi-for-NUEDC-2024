import time
from machine import UART

import bluetooth,ble_simple_peripheral
from servo import Servo

# 创建串口对象
uart = UART(1, 115200, rx=21, tx=20)  # 设置串口号1和波特率
uart.write("Hello 01Studio!")  # 发送一条数据

# 创建BLE对象
ble = bluetooth.BLE() # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble,name='WalnutPi')

def on_rx(msg):
    global text

    text = msg.decode("ascii")
    
    print("RX:",msg) #打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ") 
    peer.send(text)
    
peer.on_write(on_rx) #从机接收回调函数，收到数据会进入on_rx函数。

# 创建舵机对象
servo_x = Servo(5)
servo_x.set_limit(30,150)

servo_y = Servo(6)
servo_y.set_limit(60,120)

# 创建缓冲区
buffer = b""  # 创建一个缓冲区
frame_header = b'['  # 定义帧头
frame_footer = b']'  # 定义帧尾

text = ''

while True:
    # 判断有无收到信息    
    if uart.any():
        
        text = uart.read(128)  # 接收128个字符
        buffer += text  # 将接收到的数据添加到缓冲区
        
                # 检查是否接收到完整的数据帧
        if frame_header in buffer and frame_footer in buffer:
            # 提取完整的数据帧
            start_index = buffer.index(frame_header)
            end_index = buffer.index(frame_footer) + 1  # 包括帧尾
            complete_frame = buffer[start_index:end_index]
            
            # 解码并打印接收到的数据
            decoded_data = complete_frame.decode("ascii")
            print("接收到的数据:", decoded_data)
        
            # 去掉方括号并分割字符串
            decoded_data = decoded_data.strip('[]')  # 去掉方括号
            values = decoded_data.split(",")  # 使用 split 方法分割字符串

            try:
                angle_dx = -float(values[0].strip())  
                angle_dy = float(values[1].strip())
            
                
                angle_x = -float(values[2].strip())  
                angle_y = float(values[3].strip())
                
            except ValueError:
                print("Invalid data")

            print(f"{angle_dx}, {angle_dy}")

            if angle_dx:
                servo_x.set_angle_relative(angle_dx)

            if angle_dy:
                servo_y.set_angle_relative(angle_dy)
                
            if angle_x:
                servo_x.set_angle(angle_x)

            if angle_y:
                servo_y.set_angle(angle_y)
                
            buffer = buffer[end_index:]  # 保留未处理的数据
            
            uart.write(f"收到 {angle_dx}, {angle_dy}, {angle_x}, {angle_y}")  # 发送一条数据
