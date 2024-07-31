import time

from machine import UART, Pin  # type: ignore
from servo import Servo

uart = UART(1, 115200, rx=8, tx=7)  # 设置串口号1和波特率
uart.write("Hello 01Studio!")  # 发送一条数据

servo = Servo(5)
points = []

def fun(KEY):
    points.append(int(servo.targe_angle))
    print(f'检测到 {points}')

KEY = Pin(6, Pin.IN, Pin.PULL_UP) #构建KEY对象
KEY.irq(fun, Pin.IRQ_FALLING or Pin.IRQ_RISING) #定义中断，下降沿触发

def find_valid_average(data):
    if not data:
        print("数据为空，无法计算平均值。")
        return None

    data.sort()  # 排序数据
    n = len(data)

    # 自适应窗口大小和密度阈值
    window_size = max(1, n // 2)  # 窗口大小为数据量的一半
    density_threshold = max(1, n // 2)  # 密度阈值为数据量的一半

    valid_data = []  # 存储有效数据
    for point in data:
        # 计算在窗口内的数据数量
        count = sum(1 for x in data if point - window_size / 2 <= x <= point + window_size / 2)
        if count >= density_threshold:  # 修改为大于等于
            valid_data.append(point)

    if valid_data:  # 计算有效数据的平均值
        print("有效数据为:", valid_data)
        average = sum(valid_data) / len(valid_data)
        print(f"有效数据的平均值为: {average:.2f}")
        return average
    else:
        print("没有有效数据可计算平均值。")
        return None


max_angle  = 150
min_angle  = 30
step_speed = 5

while True:
    for i in range(min_angle*10, max_angle*10, step_speed):
        servo.set_angle(i/10)
        time.sleep(0.005)

    for i in range(max_angle*10, min_angle*10, -step_speed):
        servo.set_angle(i/10)
        time.sleep(0.005)
    
    #print(f'\n {points}')

    avg = find_valid_average(points)
    points = [] 
    print(f'\n avg: {avg}')

    
    # 在发送数据之前，确保 avg 是一个字符串
    if avg is not None:
        uart.write(str(avg))  # 将 avg 转换为字符串并发送
    else:
        uart.write("No valid average")  # 如果没有有效的平均值，发送提示信息

    time.sleep(0.5)