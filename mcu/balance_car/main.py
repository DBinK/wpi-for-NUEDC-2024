import time
from machine import UART
import bluetooth, ble_simple_peripheral

from imu import Accel
from encoder import HallEncoder
from motor import Motor
from pid import PID

IMU_OFFSET = 0.0
BASE_PWM = 90

# 创建传感器对象
imu = Accel(9, 8)
encoder_l = HallEncoder(7, 10)
encoder_r = HallEncoder(6, 5)

# 创建电机对象
motor = Motor(3, 4, 2, 1, BASE_PWM)

# 创建PID对象
pid = PID(Kp=0.1, Ki=0, Kd=0.00000001, setpoint=0, output_limits=(-1023, 1023))

# 创建BLE对象
ble = bluetooth.BLE()  # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble, name="WalnutPi")


def on_rx(msg):
    global text

    text = msg.decode("ascii")

    print("RX:", msg)  # 打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ")
    peer.send(text)


peer.on_write(on_rx)  # 从机接收回调函数，收到数据会进入on_rx函数。


while True:
    roll, pitch, _ = imu.get_angles()

    speed_l = encoder_l.get_speed()
    speed_r = encoder_r.get_speed()

    if abs(pitch) > 8 or abs(roll) > 45:
        motor.stop()
        print(f"检测到跌倒, 关闭电机, roll = {roll}, pitch = {pitch}")
        continue

    roll_fix = roll - IMU_OFFSET

    v_linear = (roll_fix / 90) * 1023
    w_angular = 0

    v_linear_pid = -pid(v_linear)

    motor.move(v_linear_pid, w_angular)

    uart_msg = f"{roll_fix}, {v_linear}, {w_angular}, {speed_l}, {speed_r}\n"

    ble_msg  = f"roll_fix: {roll_fix}, v: {v_linear}, w: {w_angular}, speed_l: {speed_l}, speed_r: {speed_r}\n"

    print(uart_msg)
    peer.send(ble_msg)

    time.sleep(0.1)
