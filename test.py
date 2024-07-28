# 标准库
import cv2
import time
import serial
import threading
import numpy as np
from loguru import logger

# 导入自定义模块
from modules.camera import Camera
from modules.point_detector import PointDetector

# cam = Camera()  # 实例化Camera类
# cap = cam.VideoCapture()  # 测试摄像头
cap = cv2.VideoCapture(2)  # 测试摄像头

if cap is not None:
    while True:
        ret, frame = cap.read()
        if ret:
            # 初始化点检测器
            point_detector = PointDetector()

            # 点检测结果
            red_point, green_point = point_detector.detect(frame)
            img_detected = point_detector.draw(frame)  # 绘制检测结果

            cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()
