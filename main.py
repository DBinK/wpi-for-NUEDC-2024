# 标准库
import cv2
import time
import platform
import threading
import numpy as np
from loguru import logger
import serial

# 导入自定义模块
from modules.camera import Camera
from modules.line_follow import LineFollower
from modules.streamer import Streamer

# 创建各类对象
cam           = Camera(400,80) 
line_follower = LineFollower()
streamer      = Streamer()

if platform.node() == 'WalnutPi':               # 开发板设备名
    com = serial.Serial('/dev/ttyS4', 115200)   # 开发板串口
# else:
#     com = serial.Serial('/dev/ttyUSB0', 115200) # 开发机器串口

lock = threading.Lock()

# 初始化变量
running = 1

base_speed = 160
ph = 0.2
pl = 0
pa = 0

def update_variable(var_name, default_value, conversion_func=float):
    if streamer.variables[var_name] is not None:
        return conversion_func(streamer.variables[var_name])
    else:
        streamer.variables[var_name] = default_value
        return default_value

# 摄像头处理线程
def process_camera_data():
    global base_speed, ph, pl, pa  # 声明使用全局变量

    cap = cam.VideoCapture()

    logger.info('正在初始化摄像头...')
    logger.info(cap)

    # 计算FPS（每秒帧率参数）
    start = 0
    end   = 0

    while True:
        start = time.time()

        ret, img = cap.read() # 从摄像头中实时读取图像
        # img = cv2.rotate(img, cv2.ROTATE_180) # 旋转图像 180 度

        if ret:

            center_h, center_l, angle = line_follower.detect(img)       # 获取巡线中心点
            drawed_frame = line_follower.draw(img, center_h, center_l)  # 绘制巡线中心点

            # cv2.namedWindow("src_frame", cv2.WINDOW_NORMAL)
            # cv2.setMouseCallback("src_frame", line_follower.get_color)
            # cv2.imshow("src_frame", line_follower.src_frame)

            # cv2.namedWindow("drawed_frame", cv2.WINDOW_NORMAL)
            # cv2.imshow("drawed_frame", drawed_frame)

            end = time.time()

            # 计算FPS(每秒帧率), 结果取整数
            fps = 1/(end-start)
            cv2.putText(drawed_frame, "FPS: "+ str(fps), (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if running == 1:
                # 设置电机速度
                l_motor = int(base_speed + (center_h*ph + center_l*pl + angle*pa))
                r_motor = int(base_speed - (center_h*ph + center_l*pl + angle*pa))
            else:
                l_motor = 0
                r_motor = 0

            # 发送数据到 streamer
            with lock:
                streamer.update(drawed_frame)  # 更新流媒体服务器的图像

                # 只读数据
                streamer.variables["center_l"] = center_l
                streamer.variables["center_h"] = center_h
                streamer.variables["angle"]    = round(angle,2)

                streamer.variables["l_motor"]  = l_motor
                streamer.variables["r_motor"]  = r_motor

                # 从 streamer 更新数据
                running = update_variable("running", running, int)
                line_follower.sample_line_pos_h = update_variable("sample_line_pos_h", line_follower.sample_line_pos_h)
                line_follower.sample_line_pos_l = update_variable("sample_line_pos_l", line_follower.sample_line_pos_l)
                base_speed = update_variable("base_speed", base_speed, int)
                ph = update_variable("ph", ph)
                pl = update_variable("pl", pl)
                pa = update_variable("pa", pa)
                

            # 发送数据到串口
            if center_l != None:  # 示例数据： [111,245,456]
                com.write(f'[{center_l},{center_h},{angle},{l_motor},{r_motor}]'.encode('ascii'))
                logger.info(f'发送到串口的数据: {l_motor}, {r_motor}')

        else:
            logger.error('读取摄像头失败')
            # 创建一个500x500像素大小的蓝色图像
            default_frame = np.full((500, 500, 3), (255, 0, 0), dtype=np.uint8) 
            streamer.update(default_frame)

        time.sleep(0.01)

# 创建一个线程来处理摄像头数据
logger.info('正在启动摄像头处理线程...')
process_camera = threading.Thread(target=process_camera_data)
process_camera.start()

# 启动Flask服务器
logger.info('正在启动Flask服务器...')
streamer.run()
