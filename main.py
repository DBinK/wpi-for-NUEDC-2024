import cv2
import time
import platform
import threading
import numpy as np
from loguru import logger
import serial

import camera
from line_follow import LineFollower
from streamer import Streamer  

cam           = camera.Camera(400,80)
line_follower = LineFollower()
streamer      = Streamer()

if platform.node() == 'WalnutPi':
    com = serial.Serial('/dev/ttyS2', 115200)
else:
    com = serial.Serial('/dev/ttyUSB0', 115200)

# 定义一个函数来处理摄像头数据
def process_camera_data():

    cap = cam.VideoCapture()

    logger.info('正在初始化摄像头...')

    if not cap.isOpened():
        logger.error('无法打开摄像头设备')
        return

    logger.info(cap)

    # 降低分辨率以提高识别速度
    # cap.set(3, 480) # 设置采集图像宽为480
    # cap.set(4, 320) # 设置采集图像高为320

    # 计算FPS（每秒帧率参数）
    start = 0
    end = 0

    while True:
        start = time.time()

        ret, img = cap.read() # 从摄像头中实时读取图像
        # img = cv2.rotate(img, cv2.ROTATE_180) # 旋转图像 180 度

        if ret:
            # # 检测出所有人脸
            # faces = faceCascade.detectMultiScale(img, 1.2)
            # #logger.info(f'faces: {faces}')

            # # 遍历所有人脸结果
            # for (x, y, w, h) in faces:
            #     cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3) # 人脸画框

            center_h, center_l, angle = line_follower.detect(img)              # 获取巡线中心点
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

            # 更新流媒体服务器的图像
            streamer.update(drawed_frame)

            if center_l != None:
                # 发送数据到串口
                com.write(f'{center_l}, {center_h}, {angle}'.encode('ascii'))

        else:
            logger.error('读取摄像头失败')
            # 创建一个500x500像素大小的蓝色图像
            default_frame = np.full((500, 500, 3), (255, 0, 0), dtype=np.uint8) 
            streamer.update(default_frame)

        time.sleep(0.01)

# 创建一个线程来处理摄像头数据
process_camera = threading.Thread(target=process_camera_data)
process_camera.start()

# 启动Flask服务器
streamer.run()

