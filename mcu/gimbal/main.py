from machine import UART
from servo import Servo

uart = UART(1, 115200, rx=2, tx=1)  # 设置串口号1和波特率
uart.write("Hello 01Studio!")  # 发送一条数据

servo_x = Servo(47)
servo_y = Servo(48)

angle_dx = None
angle_dy = None
from machine import UART
from servo import Servo

uart = UART(1, 115200, rx=2, tx=1)  # 设置串口号1和波特率
uart.write("Hello 01Studio!")  # 发送一条数据

servo_x = Servo(47)
servo_y = Servo(48)

buffer = b""  # 创建一个缓冲区
frame_header = b'['  # 定义帧头
frame_footer = b']'  # 定义帧尾

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
                angle_dx = float(values[0].strip())  
                angle_dy = float(values[1].strip())
                
            except ValueError:
                print("Invalid data")

            print(f"{angle_dx}, {angle_dy}")

            if angle_dx:
                servo_x.set_angle(angle_dx)
            
            if angle_dy:
                servo_y.set_angle(angle_dy)
                
            buffer = buffer[end_index:]  # 保留未处理的数据
