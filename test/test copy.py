import json
import serial
import time

# 假设这些是你的数据
center_h = 100
center_l = 50
angle = 30

# 将数据打包成字典
data = {
    "center_h": center_h,
    "center_l": center_l,
    "angle": angle
}

# 将字典转换为 JSON 字符串
json_data = json.dumps(data)

# 设置串口参数
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)  # 根据实际情况修改串口号和波特率
time.sleep(2)  # 等待串口稳定

# 发送 JSON 数据
ser.write(json_data.encode('utf-8'))  # 编码为 UTF-8
ser.write(b'\n')  # 发送换行符以标识数据结束

# 关闭串口
ser.close()