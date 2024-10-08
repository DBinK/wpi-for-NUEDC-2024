import time
from machine import UART
import bluetooth, ble_simple_peripheral

from imu import Accel
from encoder import HallEncoder
from motor import Motor
from pid import PID


IMU_OFFSET = 0.0
BASE_PWM = 50

# 创建传感器对象
imu = Accel(9, 8)
encoder_l = HallEncoder(7, 10)
encoder_r = HallEncoder(6, 5)

# 创建电机对象
motor = Motor(3, 4, 2, 1, BASE_PWM)

# 创建PID对象
pid = PID(kp=0.8, ki=0, kd=0.001, setpoint=0, output_limits=(-1023, 1023))

# 创建BLE对象
ble = bluetooth.BLE()  # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble, name="WalnutPi")


def on_rx(msg):
    global text

    #text = msg.decode("utf-8")

    print("RX:", msg)  # 打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ")
    peer.send(msg)

peer.on_write(on_rx)  # 从机接收回调函数，收到数据会进入on_rx函数。


while True:
    roll, pitch, _ = imu.get_angles()

    speed_l = encoder_l.get_speed()
    speed_r = encoder_r.get_speed()

    if abs(pitch) > 8 or abs(roll) > 45:
        motor.stop()
        # print(f"检测到跌倒, 关闭电机, roll = {roll}, pitch = {pitch}")
        continue

    angle = roll - IMU_OFFSET

    v_pwm = (angle / 90) * 1023
    w_pwm = 0

    v_pwm_pid = -pid.update(v_pwm)

    motor.motion(v_pwm_pid, w_pwm)

    vofa_msg = f"{angle}, {speed_l}, {speed_r}, {v_pwm}, {w_pwm}\n"

    print(vofa_msg)

    # peer.send(status_msg)

    time.sleep(0.1)
