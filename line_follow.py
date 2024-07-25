#!/usr/bin/env python3

import cv2
import numpy as np
import time
from loguru import logger
import camera

class LineFollower:
    def __init__(self):
        """
        初始化巡线计算类，设置摄像头设备。
        :param camera_device: 摄像头设备ID，默认为0。
        """
        self.src_frame = None
        self.processed_frame = None
        self.line_color = [(  0,   0,   0), (180, 255,  46)] # 巡线颜色范围
        self.site_color = [(  0,   0, 200), (180,  30, 255)] # 场地颜色范围
        self.sample_line_pos1 = 0.20
        self.sample_line_pos2 = 0.80


    # def pre_process(self, frame):
    #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #     ret, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    #     dst = cv2.dilate(dst, None, iterations=2)
    #     dst = cv2.erode(dst, None, iterations=6)
    #     self.processed_frame = dst

    def pre_process(self, frame):
        """
        对输入的帧进行预处理，包括创建蒙版并应用蒙版来突出显示感兴趣的区域。
        """
        cv2.imshow('org', frame)

        # 将BGR图像转换为HSV图像
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 定义一个内部函数create_mask，用于根据颜色范围创建蒙版
        def create_mask(image, color_range):
            lower_bound = np.array(color_range[0])
            upper_bound = np.array(color_range[1])
            mask = cv2.inRange(image, lower_bound, upper_bound)
            return mask
        
        # 根据线路颜色范围创建蒙版
        site_mask = create_mask(hsv, self.site_color)
        line_mask = create_mask(hsv, self.line_color)

        cv2.imshow('site_mask', site_mask)
        cv2.imshow('line_mask', line_mask)
        
        # 对场地蒙版进行位运算取反，以突出显示场地外的区域
        inverted_site_mask = cv2.bitwise_not(site_mask)
        
        # 通过位或运算结合线路蒙版和取反的场地蒙版，得到最终的蒙版
        final_mask = cv2.bitwise_or(line_mask, inverted_site_mask)
        
        # 显示最终的蒙版图像
        #cv2.imshow('final_mask.png', final_mask)

        return final_mask
    
    def detect_line(self, processed_frame):
        def find_center(sample_line_pos):
            color = processed_frame[sample_line_pos]
            try:
                # 找到白色的像素点个数，如寻黑色，则改为0
                white_count = np.sum(color == 0)
                # 找到白色的像素点索引，如寻黑色，则改为0
                white_index = np.where(color == 0)
                # 防止white_count=0的报错
                if white_count == 0:
                    white_count = 1
                # 找到黑色像素的中心点位置
                # 计算方法应该是边缘检测，计算白色边缘的位置和/2，即是白色的中央位置。
                center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
                # 计算出center与标准中心点的偏移量，因为图像大小是640，因此标准中心是320，因此320不能改。
                direction = center - 320
                print(direction)    
            except:
                direction = -1

            return direction
        
        # 得到图像高宽

        height, width = processed_frame.shape[:2]
        
        center_h = find_center(self.sample_line_pos1 * height)
        center_l = find_center(self.sample_line_pos2 * height)

        return center_h, center_l
        
        
    def detect(self, frame):
        processed_frame = self.pre_process(frame)
        center_h, center_l =self.detect_line(processed_frame)

        logger.debug("center_h: %s, center_l: %s", center_h, center_l)

        return center_h, center_l
    
    def draw(self, frame, center_h, center_l):
        drawed_frame = frame.copy()
        if center_h != -1:
            cv2.line(drawed_frame, (center_h, 0), (center_h, 480), (0, 0, 255), 2)
            cv2.circle(drawed_frame, (center_h, 240), 5, (0, 0, 255), -1)
        if center_l != -1:
            cv2.line(drawed_frame, (center_l, 0), (center_l, 480), (0, 0, 255), 2)
            cv2.circle(drawed_frame, (center_l, 240), 5, (0, 0, 255), -1)
        return drawed_frame
    
    def test(self):
        """
        连续读取摄像头帧并处理，用于实时巡线。
        """
        cap = cv2.VideoCapture(0)
        # 设置摄像头曝光

        logger.info(f"exposure: {cap.get(cv2.CAP_PROP_EXPOSURE)}") 

        while True:
            ret, frame = cap.read()
            if ret:
                frame = self.pre_process(frame)
                cv2.imshow("frame", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
        cap.release()

# 使用示例
if __name__ == "__main__":
    line_follower = LineFollower()
    line_follower.test()