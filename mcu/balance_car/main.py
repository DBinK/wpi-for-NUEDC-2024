import time
from machine import UART
import bluetooth,ble_simple_peripheral

from imu import Accel
from encoder import HallEncoder
from motor import Motor

IMU_OFFSET = 0.0
BASE_PWM = 300

# 创建BLE对象
ble  = bluetooth.BLE() # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble,name='WalnutPi')

def on_rx(msg):
    global text

    text = msg.decode("ascii")
    
    print("RX:",msg) #打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ") 
    peer.send(text)
    
peer.on_write(on_rx) #从机接收回调函数，收到数据会进入on_rx函数。

# 创建传感器对象
imu       = Accel(9,8)
encoder_l = HallEncoder(pin_a=2, pin_b=1)
encoder_r = HallEncoder(pin_a=3, pin_b=4)  

# 创建电机对象
motor = Motor(6,5,7,10,BASE_PWM)

while True:
    roll, pitch, yaw = imu.get_angles()

    roll_fix = roll - IMU_OFFSET

    speed_l = encoder_l.get_speed()
    speed_r = encoder_r.get_speed()

    v = (roll_fix/90) * 1023
    w = 0

    motor.move(v, w)

    uart_msg = f"{roll_fix}, {v}, {w}, {speed_l}, {speed_r}\n"
    ble_msg  = f"{roll_fix}, {v}, {w}, {speed_l}, {speed_r}\n"

    print(uart_msg)
    peer.send(ble_msg)

    time.sleep(0.1)

