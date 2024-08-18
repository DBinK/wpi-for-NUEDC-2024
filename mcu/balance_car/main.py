import time
from machine import UART
import bluetooth, ble_simple_peripheral, usocket, _thread

from imu import Accel
from encoder import HallEncoder
from motor import Motor
from pid import PID
from wifi import WIFI_Connect

IMU_OFFSET = 0.0
BASE_PWM = 50

imu = Accel(9, 8)
encoder_l = HallEncoder(7, 10)
encoder_r = HallEncoder(6, 5)
motor = Motor(3, 4, 2, 1, BASE_PWM)

pid = PID(kp=0.8, ki=0, kd=0.001, setpoint=0, output_limits=(-1023, 1023))

ble = bluetooth.BLE()  # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble, name="WalnutPi")

def on_rx(msg):
    global text

    #text = msg.decode("utf-8")

    print("RX:", msg)  # 打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ")
    peer.send(msg)

peer.on_write(on_rx)  # 从机接收回调函数，收到数据会进入on_rx函数。

tcp = usocket.socket()
tcp.connect(('192.168.1.19', 1234))  # 服务器IP和端口
tcp.send(b'Hello WalnutPi!')

def tcp_thread():
    global tcp
    while True:
        try:
            text = tcp.recv(128)  # 单次最多接收128字节
            if text:
                print("RX:", text)
                tcp.send(b'I got: ' + text)
        except Exception as e:
            print("TCP Error:", e)
            break

# 启动TCP线程
_thread.start_new_thread(tcp_thread, ())
    

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

    try:
        tcp.send(tcp_msg)#.encode('utf-8'))
    except Exception as e:
        print("Send Error:", e)

    time.sleep(0.1)

