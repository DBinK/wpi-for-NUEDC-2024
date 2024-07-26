import cv2
import time
import threading
import numpy as np
from loguru import logger

import camera
from streamer import Streamer  

streamer = Streamer()

# 定义一个函数来处理摄像头数据
def process_camera_data():
    # 加载人脸检测级联分离器
    faceCascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

    cam = camera.Camera(100,80)
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

        img = cv2.rotate(img, cv2.ROTATE_180) # 旋转图像 180 度

        if ret:
            # 检测出所有人脸
            faces = faceCascade.detectMultiScale(img, 1.2)
            #logger.info(f'faces: {faces}')

            # 遍历所有人脸结果
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3) # 人脸画框

            end = time.time()

            # 计算FPS(每秒帧率), 结果取整数
            fps = round(1/(end-start))
            #logger.info(f'fps: {fps}')

            # 图像上写字符
            cv2.putText(img, "FPS: "+ str(fps), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)

            # 更新流媒体服务器的图像
            streamer.update(img)

        else:
            logger.error('读取摄像头失败')
            # 创建一个500x500像素大小的蓝色图像
            default_frame = np.full((500, 500, 3), (255, 0, 0), dtype=np.uint8) 
            streamer.update(default_frame)

# 创建一个线程来处理摄像头数据
process_camera = threading.Thread(target=process_camera_data)
process_camera.start()

# 启动Flask服务器
streamer.run()

