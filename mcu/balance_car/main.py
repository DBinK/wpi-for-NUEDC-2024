import time
from machine import UART
import bluetooth, ble_simple_peripheral, usocket, _thread

from imu import Accel
from encoder import HallEncoder
from motor import Motor
from pid import PID
from wifi import check_network

IMU_OFFSET = 0.0
BASE_PWM = 60

imu = Accel(9, 8)
encoder_l = HallEncoder(7, 10)
encoder_r = HallEncoder(6, 5)
motor = Motor(3, 4, 2, 1, BASE_PWM)

pid = PID(kp=0.8, ki=0, kd=0.0, setpoint=0, output_limits=(-1023, 1023))

ble = bluetooth.BLE()  # 构建BLE对象
peer = ble_simple_peripheral.BLESimplePeripheral(ble, name="WalnutPi")

def on_rx(msg):
    global text

    #text = msg.decode("utf-8")

    print("RX:", msg)  # 打印接收到的数据,数据格式为字节数组。
    peer.send("I got: ")
    peer.send(msg)

peer.on_write(on_rx)  # 从机接收回调函数，收到数据会进入on_rx函数。

try:
    tcp = usocket.socket()
    tcp.connect(('192.168.1.6', 1234))  # 服务器IP和端口
    tcp.send(b'Hello WalnutPi!')

except Exception as e:
    print("TCP Error:", e)

def tcp_thread():
    global tcp, IMU_OFFSET, BASE_PWM
    while True:
        try:
            text = tcp.recv(128)  # 单次最多接收128字节
            if text:
                print("RX:", text)
                # 将字节串解码为字符串
                decoded_data = text.decode('utf-8').strip()  # 去掉末尾的换行符
                key, value = decoded_data.split(':')  # 分割字符串以提取键和值
                tcp.send(b'I got: ' + key + value)

                if key == 'kp':
                    pid.kp = float(value)
                elif key == 'ki':
                    pid.ki = float(value)
                elif key == 'kd':
                    pid.kd = float(value)
                elif key == 'offset':
                    IMU_OFFSET = float(value)
                elif key == 'BASE_PWM':
                    BASE_PWM = int(value)
                    motor.BASE_SPEED = BASE_PWM         
                
        except Exception as e:
            print("TCP Error:", e)
            break

# 启动TCP线程
_thread.start_new_thread(tcp_thread, ())

delay_s_max = 0

while True:

    start = time.ticks_us()

    roll, pitch = imu.get_angles()

    speed_l = encoder_l.get_speed()
    speed_r = encoder_r.get_speed()

    if abs(pitch) > 15 or abs(roll) > 60:
        motor.stop()
        print(f"检测到跌倒, 关闭电机, roll = {roll}, pitch = {pitch}")
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
        tcp.send(vofa_msg)#.encode('utf-8'))
    except Exception as e:
        print("Send Error:", e)

    time.sleep(0.0001)

    end = time.ticks_us()

    delay_s = (end - start) / 1000000

    delay_s_max = max(delay_s_max, delay_s)

    print(f"delay: {delay_s}, delay_s_max: {delay_s_max}")
